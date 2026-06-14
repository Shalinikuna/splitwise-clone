from django.contrib import admin
from .models import Expense, ExpenseSplit


class ExpenseSplitInline(admin.TabularInline):
    model = ExpenseSplit
    extra = 0
    readonly_fields = ["amount", "share_input"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["title", "amount", "group", "paid_by", "split_type", "created_at"]
    list_filter = ["split_type"]
    search_fields = ["title"]
    inlines = [ExpenseSplitInline]


@admin.register(ExpenseSplit)
class ExpenseSplitAdmin(admin.ModelAdmin):
    list_display = ["expense", "user", "amount", "share_input"]
