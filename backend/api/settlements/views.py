from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from api.groups.models import Group, GroupMember
from .models import Settlement

User = get_user_model()


class SettlementUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "name")


class SettlementSerializer(serializers.ModelSerializer):
    paid_by = SettlementUserSerializer(read_only=True)
    paid_to = SettlementUserSerializer(read_only=True)

    class Meta:
        model = Settlement
        fields = ("id", "group", "paid_by", "paid_to", "amount", "note", "created_at")


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def settlement_list_create(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        return Response({"detail": "Not a member."}, status=403)

    if request.method == "GET":
        settlements = Settlement.objects.filter(group=group).select_related(
            "paid_by", "paid_to"
        ).order_by("-created_at")
        return Response(SettlementSerializer(settlements, many=True).data)

    # POST — record a settlement
    paid_to_id = request.data.get("paid_to_id")
    amount = request.data.get("amount")
    note = request.data.get("note", "")

    if not paid_to_id or not amount:
        return Response({"detail": "paid_to_id and amount required."}, status=400)

    try:
        paid_to = User.objects.get(id=paid_to_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=404)

    settlement = Settlement.objects.create(
        group=group,
        paid_by=request.user,
        paid_to=paid_to,
        amount=amount,
        note=note,
    )
    return Response(SettlementSerializer(settlement).data, status=201)
