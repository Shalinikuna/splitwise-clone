from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from api.groups.models import Group, GroupMember
from .models import Expense
from .serializers import ExpenseSerializer, ExpenseCreateSerializer
from .balance import compute_group_balance_matrix, compute_overall_balance


def assert_group_member(group_id, user):
    group = get_object_or_404(Group, id=group_id)
    if not GroupMember.objects.filter(group=group, user=user).exists():
        return None, Response({"detail": "Not a member."}, status=403)
    return group, None


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def expense_list_create(request, group_id):
    group, err = assert_group_member(group_id, request.user)
    if err:
        return err

    if request.method == "GET":
        expenses = Expense.objects.filter(group=group).select_related(
            "paid_by", "created_by"
        ).prefetch_related("splits__user").order_by("-created_at")
        return Response(ExpenseSerializer(expenses, many=True).data)

    serializer = ExpenseCreateSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    expense = serializer.create(serializer.validated_data, group)
    return Response(ExpenseSerializer(expense).data, status=201)


@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def expense_detail(request, expense_id):
    expense = get_object_or_404(
        Expense.objects.select_related("paid_by", "created_by").prefetch_related("splits__user"),
        id=expense_id,
    )
    group, err = assert_group_member(expense.group_id, request.user)
    if err:
        return err

    if request.method == "GET":
        return Response(ExpenseSerializer(expense).data)

    if request.method == "DELETE":
        expense.delete()
        return Response(status=204)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def group_balances(request, group_id):
    group, err = assert_group_member(group_id, request.user)
    if err:
        return err
    return Response(compute_group_balance_matrix(group))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_overall_balances(request):
    return Response(compute_overall_balance(request.user))
