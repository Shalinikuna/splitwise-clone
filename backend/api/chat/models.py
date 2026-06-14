import uuid
from django.db import models
from django.conf import settings
from api.expenses.models import Expense


class ExpenseComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "chat"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.name}: {self.text[:40]}"
