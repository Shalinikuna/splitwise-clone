from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import json
from datetime import datetime

from .engine import run_import
from .models import ImportSession, ImportAnomaly, ImportedExpense, ImportedSettlement


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, JSONParser])
def upload_csv(request):
    """
    POST /api/import/upload/
    Accepts multipart file upload with key 'file'.
    Returns full import report with anomalies.
    """
    file_obj = request.FILES.get("file")
    if not file_obj:
        return Response({"detail": "No file uploaded. Send CSV as 'file'."}, status=400)

    if not file_obj.name.endswith(".csv"):
        return Response({"detail": "Only CSV files are accepted."}, status=400)

    try:
        csv_text = file_obj.read().decode("utf-8-sig")  # handle BOM
    except UnicodeDecodeError:
        return Response({"detail": "Could not decode CSV. Ensure it is UTF-8."}, status=400)

    # Run anomaly detection engine
    result = run_import(csv_text)

    # Persist to DB
    session = ImportSession.objects.create(
        imported_by=request.user,
        filename=file_obj.name,
        status="complete",
        total_rows=result["summary"]["total_rows"],
        imported_rows=result["summary"]["imported"],
        skipped_rows=result["summary"]["skipped"],
        anomaly_count=result["summary"]["anomaly_count"],
    )

    # Save anomalies
    anomaly_objs = [
        ImportAnomaly(
            session=session,
            row_number=a["row"],
            code=a["code"],
            message=a["message"],
            severity=a["severity"],
            raw_description=a.get("raw_description", ""),
        )
        for a in result["anomalies"]
    ]
    ImportAnomaly.objects.bulk_create(anomaly_objs)

    # Save imported expenses
    expense_objs = []
    for row in result["imported"]:
        expense_objs.append(ImportedExpense(
            session=session,
            row_number=row["row"],
            date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
            description=row["description"],
            paid_by=row["paid_by"],
            amount_original=row["amount_original"],
            currency_original=row["currency_original"],
            amount_inr=row["amount_inr"],
            split_type=row["split_type"],
            split_with=row["split_with"],
            split_details={str(k): str(v) for k, v in row["split_details"].items()},
            notes=row["notes"],
            is_refund=row["is_refund"],
            has_anomaly=row["has_anomaly"],
        ))
    ImportedExpense.objects.bulk_create(expense_objs)

    # Save settlements
    settlement_objs = []
    for s in result["settlements"]:
        settlement_objs.append(ImportedSettlement(
            session=session,
            row_number=s["row"],
            date=datetime.strptime(s["date"], "%Y-%m-%d").date(),
            description=s["description"],
            paid_by=s["paid_by"],
            paid_to=s.get("paid_to", ""),
            amount_inr=s["amount_inr"],
            notes=s.get("notes", ""),
        ))
    ImportedSettlement.objects.bulk_create(settlement_objs)

    return Response({
        "session_id": str(session.id),
        "summary": result["summary"],
        "anomalies": result["anomalies"],
        "imported": result["imported"],
        "settlements": result["settlements"],
        "skipped": result["skipped"],
    }, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_sessions(request):
    """GET /api/import/sessions/ — list all import sessions."""
    sessions = ImportSession.objects.filter(imported_by=request.user)
    data = [
        {
            "id": str(s.id),
            "filename": s.filename,
            "status": s.status,
            "total_rows": s.total_rows,
            "imported_rows": s.imported_rows,
            "skipped_rows": s.skipped_rows,
            "anomaly_count": s.anomaly_count,
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def session_report(request, session_id):
    """GET /api/import/sessions/<id>/ — full report for one session."""
    try:
        session = ImportSession.objects.get(id=session_id, imported_by=request.user)
    except ImportSession.DoesNotExist:
        return Response({"detail": "Not found."}, status=404)

    anomalies = list(session.anomaly_records.values(
        "row_number", "code", "message", "severity", "raw_description"
    ))
    expenses = list(session.imported_expenses.values(
        "row_number", "date", "description", "paid_by",
        "amount_original", "currency_original", "amount_inr",
        "split_type", "split_with", "notes", "is_refund", "has_anomaly"
    ))
    settlements = list(session.imported_settlements.values(
        "row_number", "date", "description", "paid_by", "paid_to", "amount_inr", "notes"
    ))

    return Response({
        "session": {
            "id": str(session.id),
            "filename": session.filename,
            "status": session.status,
            "total_rows": session.total_rows,
            "imported_rows": session.imported_rows,
            "skipped_rows": session.skipped_rows,
            "anomaly_count": session.anomaly_count,
            "created_at": session.created_at.isoformat(),
        },
        "anomalies": anomalies,
        "imported": expenses,
        "settlements": settlements,
    })
