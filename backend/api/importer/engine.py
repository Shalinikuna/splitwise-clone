"""
CSV Anomaly Detection & Import Engine
Handles all known data problems in Expenses_Export.csv
"""
import csv
import io
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation


# ── Name normalisation map ──────────────────────────────────────────────────
# All known aliases → canonical name
NAME_ALIASES = {
    "priya s": "Priya",
    "priya":   "Priya",
    "rohan ":  "Rohan",
    "rohan":   "Rohan",
    "aisha":   "Aisha",
    "meera":   "Meera",
    "dev":     "Dev",
    "sam":     "Sam",
}

KNOWN_MEMBERS = {"Aisha", "Rohan", "Priya", "Meera", "Dev", "Sam"}

# USD→INR fixed rate (assignment scope: no live FX)
USD_TO_INR = Decimal("84.0")


# ── Date parsers ────────────────────────────────────────────────────────────
DATE_FORMATS = [
    "%d-%m-%Y",   # 01-02-2026
    "%d-%m-%y",   # 01-02-26
    "%Y-%m-%d",   # 2026-02-01
    "%b-%d",      # Mar-14  (year assumed 2026)
    "%B-%d",      # March-14
]


def parse_date(raw: str) -> tuple[datetime | None, str | None]:
    """Return (datetime, warning_message_or_None)."""
    raw = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(raw, fmt)
            if dt.year == 1900:          # strptime default when year absent
                dt = dt.replace(year=2026)
                return dt, f"Date '{raw}' had no year – assumed 2026"
            return dt, None
        except ValueError:
            continue
    return None, f"Unparseable date '{raw}' – row skipped"


# ── Amount parsers ──────────────────────────────────────────────────────────
def parse_amount(raw: str) -> tuple[Decimal | None, str | None]:
    """Strip commas/quotes, handle negatives, return (Decimal, warning)."""
    cleaned = raw.strip().strip('"').replace(",", "")
    try:
        val = Decimal(cleaned)
        return val, None
    except InvalidOperation:
        return None, f"Invalid amount '{raw}'"


# ── Name normaliser ─────────────────────────────────────────────────────────
def normalise_name(raw: str) -> tuple[str, str | None]:
    key = raw.strip().lower()
    canonical = NAME_ALIASES.get(key)
    if canonical:
        warning = None if key == canonical.lower() else f"Name '{raw}' normalised to '{canonical}'"
        return canonical, warning
    # Unknown name — keep as-is but warn
    title = raw.strip().title()
    return title, f"Unknown member '{raw}' – kept as '{title}', not in KNOWN_MEMBERS"


def normalise_split_with(raw: str) -> tuple[list[str], list[str]]:
    """
    Parse semicolon-separated member list.
    Returns (clean_members, warnings).
    """
    warnings = []
    members = []
    for part in raw.split(";"):
        part = part.strip()
        if not part:
            continue
        # Handle things like "Dev's friend Kabir"
        if "'" in part or " " in part and part.lower() not in NAME_ALIASES:
            # Check if it's a known name with trailing space
            norm, w = normalise_name(part)
            if norm not in KNOWN_MEMBERS:
                warnings.append(f"Non-member '{part}' in split_with – excluded")
                continue
            members.append(norm)
            if w:
                warnings.append(w)
        else:
            norm, w = normalise_name(part)
            members.append(norm)
            if w:
                warnings.append(w)
    return members, warnings


# ── Main importer ────────────────────────────────────────────────────────────
def run_import(csv_text: str) -> dict:
    """
    Parse the CSV, detect anomalies, return structured result.

    Returns:
      {
        "imported": [...],        # clean expense rows ready for DB
        "settlements": [...],     # rows identified as settlements
        "skipped": [...],         # rows skipped with reason
        "anomalies": [...],       # all anomaly records
        "summary": {...}
      }
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)

    imported = []
    settlements = []
    skipped = []
    anomalies = []

    # Track seen (date, description_normalised, amount) for duplicate detection
    seen_fingerprints = {}

    def add_anomaly(row_num, code, message, severity="warning"):
        anomalies.append({
            "row": row_num,
            "code": code,
            "message": message,
            "severity": severity,
            "raw_description": rows[row_num - 2].get("description", "") if row_num >= 2 else "",
        })

    for i, row in enumerate(rows, start=2):  # row 1 = header
        row_anomalies = []
        skip_reason = None

        raw_date        = row.get("date", "").strip()
        raw_desc        = row.get("description", "").strip()
        raw_paid_by     = row.get("paid_by", "").strip()
        raw_amount      = row.get("amount", "").strip()
        raw_currency    = row.get("currency", "").strip()
        raw_split_type  = row.get("split_type", "").strip().lower()
        raw_split_with  = row.get("split_with", "").strip()
        raw_split_det   = row.get("split_details", "").strip()
        raw_notes       = row.get("notes", "").strip()

        # ── 1. DATE ──────────────────────────────────────────────────────────
        parsed_date, date_warn = parse_date(raw_date)
        if date_warn:
            add_anomaly(i, "DATE_FORMAT", date_warn, "warning")
            row_anomalies.append(date_warn)
        if parsed_date is None:
            skip_reason = f"Unparseable date '{raw_date}'"
            add_anomaly(i, "DATE_INVALID", skip_reason, "error")
            skipped.append({"row": i, "raw": dict(row), "reason": skip_reason})
            continue

        # Ambiguous date flag (04-05-2026 note)
        if raw_notes and ("april 5 or may 4" in raw_notes.lower() or "format is a mess" in raw_notes.lower()):
            add_anomaly(i, "DATE_AMBIGUOUS",
                        f"Date '{raw_date}' is ambiguous (dd-mm vs mm-dd) – treated as dd-mm-YYYY",
                        "warning")

        # ── 2. PAID BY ───────────────────────────────────────────────────────
        if not raw_paid_by:
            add_anomaly(i, "MISSING_PAID_BY",
                        f"Row {i} '{raw_desc}' has no paid_by – row skipped", "error")
            skipped.append({"row": i, "raw": dict(row), "reason": "Missing paid_by"})
            continue

        paid_by, pb_warn = normalise_name(raw_paid_by)
        if pb_warn:
            add_anomaly(i, "NAME_NORMALISED", pb_warn, "warning")
            row_anomalies.append(pb_warn)

        # ── 3. AMOUNT ────────────────────────────────────────────────────────
        amount, amt_warn = parse_amount(raw_amount)
        if amt_warn:
            add_anomaly(i, "AMOUNT_INVALID", amt_warn, "error")
            skipped.append({"row": i, "raw": dict(row), "reason": amt_warn})
            continue

        if amount == Decimal("0"):
            add_anomaly(i, "ZERO_AMOUNT",
                        f"Row {i} '{raw_desc}' amount is 0 – skipped (likely duplicate fix placeholder)",
                        "warning")
            skipped.append({"row": i, "raw": dict(row), "reason": "Zero amount"})
            continue

        if amount < Decimal("0"):
            add_anomaly(i, "NEGATIVE_AMOUNT",
                        f"Row {i} '{raw_desc}' has negative amount {amount} – treated as refund/credit",
                        "warning")
            row_anomalies.append("Negative amount treated as refund")

        # Comma in amount (e.g. "1,200")
        if "," in raw_amount.strip('"'):
            add_anomaly(i, "AMOUNT_COMMA",
                        f"Amount '{raw_amount}' had comma formatting – cleaned to {amount}",
                        "info")

        # ── 4. CURRENCY ──────────────────────────────────────────────────────
        currency = raw_currency.upper() if raw_currency else "INR"
        amount_inr = amount

        if not raw_currency:
            add_anomaly(i, "MISSING_CURRENCY",
                        f"Row {i} '{raw_desc}' has no currency – defaulted to INR",
                        "warning")
            row_anomalies.append("Currency defaulted to INR")

        if currency == "USD":
            amount_inr = (amount * USD_TO_INR).quantize(Decimal("0.01"))
            add_anomaly(i, "FOREIGN_CURRENCY",
                        f"Row {i} '{raw_desc}' is USD {amount} – converted to INR {amount_inr} at ₹{USD_TO_INR}/USD",
                        "info")
            row_anomalies.append(f"USD converted: {amount} USD → ₹{amount_inr}")

        # ── 5. SETTLEMENT DETECTION ──────────────────────────────────────────
        is_settlement = False
        settlement_keywords = ["paid back", "settlement", "paid aisha back", "paid rohan back",
                               "deposit share", "deposit"]
        desc_lower = raw_desc.lower()
        notes_lower = raw_notes.lower()

        if not raw_split_type and ("settlement" in notes_lower or "not an expense" in notes_lower):
            is_settlement = True
        if any(kw in desc_lower for kw in ["paid back", "paid aisha back"]):
            is_settlement = True
        if "deposit share" in desc_lower:
            is_settlement = True

        if is_settlement:
            add_anomaly(i, "IS_SETTLEMENT",
                        f"Row {i} '{raw_desc}' identified as settlement, not expense – moved to settlements table",
                        "info")
            # For settlement: split_with is "paid to"
            paid_to_raw = raw_split_with.split(";")[0].strip() if raw_split_with else ""
            paid_to, _ = normalise_name(paid_to_raw) if paid_to_raw else ("", None)
            settlements.append({
                "row": i,
                "date": parsed_date.strftime("%Y-%m-%d"),
                "description": raw_desc,
                "paid_by": paid_by,
                "paid_to": paid_to,
                "amount_original": float(amount),
                "currency": currency,
                "amount_inr": float(amount_inr),
                "notes": raw_notes,
                "anomalies": row_anomalies,
            })
            continue

        # ── 6. SPLIT TYPE ────────────────────────────────────────────────────
        valid_split_types = {"equal", "unequal", "percentage", "share", "shares"}
        if raw_split_type not in valid_split_types:
            add_anomaly(i, "INVALID_SPLIT_TYPE",
                        f"Row {i} split_type '{raw_split_type}' is not valid – defaulted to 'equal'",
                        "warning")
            raw_split_type = "equal"

        # Normalise "share" → "shares"
        if raw_split_type == "share":
            raw_split_type = "shares"

        # Contradiction: split_type=equal but split_details has weights
        if raw_split_type == "equal" and raw_split_det and any(
            c.isdigit() for c in raw_split_det
        ):
            add_anomaly(i, "SPLIT_TYPE_CONFLICT",
                        f"Row {i} '{raw_desc}': split_type=equal but split_details has weights '{raw_split_det}' – using shares",
                        "warning")
            raw_split_type = "shares"

        # ── 7. SPLIT WITH – member validation ────────────────────────────────
        split_members, sw_warns = normalise_split_with(raw_split_with)
        for w in sw_warns:
            add_anomaly(i, "MEMBER_ISSUE", w, "warning")
            row_anomalies.append(w)

        # Stale member: Meera after March (she moved out 28-03)
        if parsed_date >= datetime(2026, 4, 1) and "Meera" in split_members:
            add_anomaly(i, "STALE_MEMBER",
                        f"Row {i} '{raw_desc}': Meera is in split_with but she moved out in March – removed",
                        "warning")
            split_members = [m for m in split_members if m != "Meera"]

        # ── 8. PERCENTAGE VALIDATION ─────────────────────────────────────────
        parsed_splits = {}
        if raw_split_type == "percentage" and raw_split_det:
            total_pct = Decimal("0")
            try:
                for part in raw_split_det.split(";"):
                    part = part.strip()
                    if not part:
                        continue
                    name_part, pct_part = part.rsplit(" ", 1)
                    pct_val = Decimal(pct_part.replace("%", "").strip())
                    name_norm, _ = normalise_name(name_part.strip())
                    parsed_splits[name_norm] = pct_val
                    total_pct += pct_val

                if abs(total_pct - Decimal("100")) > Decimal("0.5"):
                    add_anomaly(i, "PCT_SUM_INVALID",
                                f"Row {i} '{raw_desc}': percentages sum to {total_pct}% (not 100%) – normalised proportionally",
                                "warning")
                    # Normalise
                    for k in parsed_splits:
                        parsed_splits[k] = (parsed_splits[k] / total_pct * 100).quantize(Decimal("0.01"))
            except Exception as e:
                add_anomaly(i, "SPLIT_DETAIL_PARSE_ERROR",
                            f"Row {i} could not parse split_details '{raw_split_det}': {e}",
                            "warning")

        elif raw_split_type == "unequal" and raw_split_det:
            try:
                total_assigned = Decimal("0")
                for part in raw_split_det.split(";"):
                    part = part.strip()
                    if not part:
                        continue
                    name_part, amt_part = part.rsplit(" ", 1)
                    amt_val = Decimal(amt_part.strip())
                    name_norm, _ = normalise_name(name_part.strip())
                    parsed_splits[name_norm] = amt_val
                    total_assigned += amt_val
                if abs(total_assigned - amount_inr) > Decimal("1"):
                    add_anomaly(i, "UNEQUAL_SUM_MISMATCH",
                                f"Row {i} '{raw_desc}': split amounts sum to {total_assigned}, expense is {amount_inr}",
                                "warning")
            except Exception as e:
                add_anomaly(i, "SPLIT_DETAIL_PARSE_ERROR",
                            f"Row {i} could not parse split_details: {e}", "warning")

        elif raw_split_type == "shares" and raw_split_det:
            try:
                for part in raw_split_det.split(";"):
                    part = part.strip()
                    if not part:
                        continue
                    name_part, share_part = part.rsplit(" ", 1)
                    share_val = Decimal(share_part.strip())
                    name_norm, _ = normalise_name(name_part.strip())
                    parsed_splits[name_norm] = share_val
            except Exception as e:
                add_anomaly(i, "SPLIT_DETAIL_PARSE_ERROR",
                            f"Row {i} could not parse split_details: {e}", "warning")

        # ── 9. DUPLICATE DETECTION ───────────────────────────────────────────
        desc_norm = re.sub(r"[^a-z0-9]", "", raw_desc.lower())
        fingerprint = (parsed_date.strftime("%Y-%m-%d"), desc_norm, str(abs(amount_inr)))

        if fingerprint in seen_fingerprints:
            prev_row = seen_fingerprints[fingerprint]
            add_anomaly(i, "DUPLICATE",
                        f"Row {i} '{raw_desc}' looks like a duplicate of row {prev_row} – skipped",
                        "error")
            skipped.append({"row": i, "raw": dict(row), "reason": f"Duplicate of row {prev_row}"})
            continue

        # Fuzzy duplicate: same date, similar description, same amount
        for fp, pr in seen_fingerprints.items():
            fp_date, fp_desc, fp_amt = fp
            if (fp_date == parsed_date.strftime("%Y-%m-%d") and
                    fp_amt == str(abs(amount_inr)) and
                    (fp_desc in desc_norm or desc_norm in fp_desc) and
                    fp_desc != desc_norm):
                add_anomaly(i, "LIKELY_DUPLICATE",
                            f"Row {i} '{raw_desc}' may be a duplicate of row {pr} (same date+amount, similar description) – imported with flag",
                            "warning")
                row_anomalies.append(f"Possible duplicate of row {pr}")
                break

        seen_fingerprints[fingerprint] = i

        # ── 10. AMOUNT PRECISION ─────────────────────────────────────────────
        if amount != amount.quantize(Decimal("0.01")) and amount > 0:
            add_anomaly(i, "AMOUNT_PRECISION",
                        f"Row {i} '{raw_desc}' amount {amount} has >2 decimal places – rounded to {amount.quantize(Decimal('0.01'))}",
                        "info")

        # ── Build clean row ──────────────────────────────────────────────────
        clean_row = {
            "row": i,
            "date": parsed_date.strftime("%Y-%m-%d"),
            "description": raw_desc,
            "paid_by": paid_by,
            "amount_original": float(amount),
            "currency_original": currency,
            "amount_inr": float(amount_inr.quantize(Decimal("0.01"))),
            "split_type": raw_split_type,
            "split_with": split_members,
            "split_details": parsed_splits,
            "notes": raw_notes,
            "is_refund": amount < 0,
            "anomalies": row_anomalies,
            "has_anomaly": len(row_anomalies) > 0,
        }
        imported.append(clean_row)

    summary = {
        "total_rows": len(rows),
        "imported": len(imported),
        "settlements": len(settlements),
        "skipped": len(skipped),
        "anomaly_count": len(anomalies),
        "anomaly_breakdown": {},
    }
    for a in anomalies:
        summary["anomaly_breakdown"][a["code"]] = summary["anomaly_breakdown"].get(a["code"], 0) + 1

    return {
        "imported": imported,
        "settlements": settlements,
        "skipped": skipped,
        "anomalies": anomalies,
        "summary": summary,
    }
