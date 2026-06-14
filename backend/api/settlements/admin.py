from django.contrib import admin
from .models import Settlement


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ["group", "paid_by", "paid_to", "amount", "note", "created_at"]
    list_filter = ["group"]
    search_fields = ["paid_by__email", "paid_to__email"]
