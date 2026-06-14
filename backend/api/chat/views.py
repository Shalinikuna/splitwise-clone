from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers, status
from django.shortcuts import get_object_or_404

from api.expenses.models import Expense
from api.groups.models import GroupMember
from .models import ExpenseComment


class CommentUserSerializer(serializers.ModelSerializer):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    class Meta:
        from django.contrib.auth import get_user_model
        model = get_user_model()
        fields = ("id", "email", "name")


class CommentSerializer(serializers.ModelSerializer):
    user = CommentUserSerializer(read_only=True)

    class Meta:
        model = ExpenseComment
        fields = ("id", "user", "text", "created_at")


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def comment_list_create(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    if not GroupMember.objects.filter(group=expense.group, user=request.user).exists():
        return Response({"detail": "Not a member."}, status=403)

    if request.method == "GET":
        comments = ExpenseComment.objects.filter(expense=expense).select_related("user")
        return Response(CommentSerializer(comments, many=True).data)

    text = request.data.get("text", "").strip()
    if not text:
        return Response({"detail": "Text required."}, status=400)
    comment = ExpenseComment.objects.create(expense=expense, user=request.user, text=text)
    return Response(CommentSerializer(comment).data, status=201)
