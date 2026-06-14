from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Expense, ExpenseSplit
from .split_logic import compute_splits

User = get_user_model()


class SplitUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "name")


class ExpenseSplitSerializer(serializers.ModelSerializer):
    user = SplitUserSerializer(read_only=True)

    class Meta:
        model = ExpenseSplit
        fields = ("id", "user", "amount", "share_input")


class ExpenseSerializer(serializers.ModelSerializer):
    splits = ExpenseSplitSerializer(many=True, read_only=True)
    paid_by = SplitUserSerializer(read_only=True)
    created_by = SplitUserSerializer(read_only=True)

    class Meta:
        model = Expense
        fields = (
            "id", "group", "title", "amount", "paid_by",
            "split_type", "splits", "created_by", "created_at",
        )


class SplitInputSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    percentage = serializers.DecimalField(max_digits=7, decimal_places=4, required=False)
    shares = serializers.DecimalField(max_digits=7, decimal_places=4, required=False)


class ExpenseCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=300)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    paid_by_id = serializers.UUIDField()
    split_type = serializers.ChoiceField(choices=["equal", "unequal", "percentage", "shares"])
    splits = SplitInputSerializer(many=True)

    def validate(self, data):
        return data

    def create(self, validated_data, group):
        splits_input = validated_data.pop("splits")
        paid_by_id = validated_data.pop("paid_by_id")

        try:
            paid_by = User.objects.get(id=paid_by_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("paid_by user not found.")

        computed = compute_splits(
            validated_data["split_type"],
            validated_data["amount"],
            [s for s in splits_input],
        )

        expense = Expense.objects.create(
            group=group,
            paid_by=paid_by,
            created_by=self.context["request"].user,
            **validated_data,
        )

        for item in computed:
            try:
                user = User.objects.get(id=item["user_id"])
            except User.DoesNotExist:
                continue
            ExpenseSplit.objects.create(
                expense=expense,
                user=user,
                amount=item["amount"],
                share_input=item["share_input"],
            )

        return expense
