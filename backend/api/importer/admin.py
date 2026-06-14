from django.contrib import admin
from .models import ImportSession, ImportAnomaly, ImportedExpense, ImportedSettlement


class AnomalyInline(admin.TabularInline):
    model = ImportAnomaly
    extra = 0
    readonly_fields = ["row_number", "code", "severity", "message"]


class ExpenseInline(admin.TabularInline):
    model = ImportedExpense
    extra = 0
    readonly_fields = ["row_number", "date", "description", "paid_by", "amount_inr", "split_type", "has_anomaly"]


@admin.register(ImportSession)
class ImportSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "filename", "status", "total_rows", "imported_rows", "skipped_rows", "anomaly_count", "created_at"]
    inlines = [AnomalyInline, ExpenseInline]


@admin.register(ImportAnomaly)
class ImportAnomalyAdmin(admin.ModelAdmin):
    list_display = ["session", "row_number", "code", "severity", "message"]
    list_filter = ["severity", "code"]


@admin.register(ImportedExpense)
class ImportedExpenseAdmin(admin.ModelAdmin):
    list_display = ["date", "description", "paid_by", "amount_inr", "split_type", "has_anomaly"]
    list_filter = ["has_anomaly", "is_refund", "split_type"]
