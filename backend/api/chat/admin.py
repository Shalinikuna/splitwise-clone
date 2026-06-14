from django.contrib import admin
from .models import ExpenseComment


@admin.register(ExpenseComment)
class ExpenseCommentAdmin(admin.ModelAdmin):
    list_display = ["expense", "user", "text", "created_at"]
    search_fields = ["user__email", "text"]
