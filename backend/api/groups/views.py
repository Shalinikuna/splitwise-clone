from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Group, GroupMember
from .serializers import GroupSerializer, GroupCreateSerializer

User = get_user_model()


def get_group_for_user(group_id, user):
    """Return group only if user is a member."""
    group = get_object_or_404(Group, id=group_id)
    if not GroupMember.objects.filter(group=group, user=user).exists():
        return None, Response({"detail": "Not a member."}, status=status.HTTP_403_FORBIDDEN)
    return group, None


class GroupListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Group.objects.filter(
            members__user=self.request.user
        ).prefetch_related("members__user").select_related("created_by")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return GroupCreateSerializer
        return GroupSerializer

    def create(self, request, *args, **kwargs):
        serializer = GroupCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        group = serializer.save()
        return Response(GroupSerializer(group).data, status=status.HTTP_201_CREATED)


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

    def get_object(self):
        group, err = get_group_for_user(self.kwargs["pk"], self.request.user)
        if err:
            raise PermissionError()
        return group

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        membership = GroupMember.objects.get(group=group, user=request.user)
        if membership.role != GroupMember.ROLE_ADMIN:
            return Response({"detail": "Only admin can delete group."}, status=403)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def invite_member(request, pk):
    group, err = get_group_for_user(pk, request.user)
    if err:
        return err

    email = request.data.get("email")
    if not email:
        return Response({"detail": "Email required."}, status=400)

    try:
        user_to_invite = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=404)

    if GroupMember.objects.filter(group=group, user=user_to_invite).exists():
        return Response({"detail": "Already a member."}, status=400)

    GroupMember.objects.create(group=group, user=user_to_invite, role=GroupMember.ROLE_MEMBER)
    return Response({"detail": "User invited successfully."}, status=201)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_member(request, pk, user_id):
    group, err = get_group_for_user(pk, request.user)
    if err:
        return err

    my_membership = GroupMember.objects.get(group=group, user=request.user)
    if my_membership.role != GroupMember.ROLE_ADMIN:
        return Response({"detail": "Only admin can remove members."}, status=403)

    target_membership = get_object_or_404(GroupMember, group=group, user__id=user_id)
    target_membership.delete()
    return Response(status=204)
