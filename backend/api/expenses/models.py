import uuid
from django.db import models
from django.conf import settings
from api.groups.models import Group


class Expense(models.Model):
    SPLIT_EQUAL = "equal"
    SPLIT_UNEQUAL = "unequal"
    SPLIT_PERCENTAGE = "percentage"
    SPLIT_SHARES = "shares"
    SPLIT_CHOICES = [
        (SPLIT_EQUAL, "Equal"),
        (SPLIT_UNEQUAL, "Unequal"),
        (SPLIT_PERCENTAGE, "Percentage"),
        (SPLIT_SHARES, "Shares"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="expenses")
    title = models.CharField(max_length=300)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="paid_expenses",
    )
    split_type = models.CharField(max_length=20, choices=SPLIT_CHOICES, default=SPLIT_EQUAL)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_expenses",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "expenses"

    def __str__(self):
        return f"{self.title} (₹{self.amount})"


class ExpenseSplit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="splits")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="expense_splits"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    share_input = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    class Meta:
        app_label = "expenses"
        constraints = [
            models.UniqueConstraint(fields=["expense", "user"], name="unique_expense_user")
        ]
