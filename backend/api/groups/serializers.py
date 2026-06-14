from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Group, GroupMember

User = get_user_model()


class MemberUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "name")


class GroupMemberSerializer(serializers.ModelSerializer):
    user = MemberUserSerializer(read_only=True)

    class Meta:
        model = GroupMember
        fields = ("id", "user", "role", "joined_at")


class GroupSerializer(serializers.ModelSerializer):
    members = GroupMemberSerializer(many=True, read_only=True)
    created_by = MemberUserSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ("id", "name", "description", "created_by", "members", "member_count", "created_at")

    def get_member_count(self, obj):
        return obj.members.count()


class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("name", "description")

    def create(self, validated_data):
        user = self.context["request"].user
        group = Group.objects.create(created_by=user, **validated_data)
        GroupMember.objects.create(group=group, user=user, role=GroupMember.ROLE_ADMIN)
        return group
