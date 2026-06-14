import uuid
from django.db import models
from django.conf import settings


class ImportSession(models.Model):
    """One CSV import run."""
    STATUS_CHOICES = [
        ("pending",   "Pending"),
        ("complete",  "Complete"),
        ("failed",    "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    filename = models.CharField(max_length=255, default="Expenses_Export.csv")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_rows    = models.IntegerField(default=0)
    imported_rows = models.IntegerField(default=0)
    skipped_rows  = models.IntegerField(default=0)
    anomaly_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "importer"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Import {self.id} — {self.status} ({self.imported_rows} rows)"


class ImportAnomaly(models.Model):
    """One detected anomaly from an import session."""
    SEVERITY_CHOICES = [
        ("info",    "Info"),
        ("warning", "Warning"),
        ("error",   "Error"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ImportSession, on_delete=models.CASCADE, related_name="anomaly_records")
    row_number  = models.IntegerField()
    code        = models.CharField(max_length=50)
    message     = models.TextField()
    severity    = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="warning")
    raw_description = models.CharField(max_length=500, blank=True)

    class Meta:
        app_label = "importer"
        ordering = ["row_number"]

    def __str__(self):
        return f"[{self.severity.upper()}] Row {self.row_number}: {self.code}"


class ImportedExpense(models.Model):
    """A successfully imported expense row, stored flat for reporting."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ImportSession, on_delete=models.CASCADE, related_name="imported_expenses")
    row_number       = models.IntegerField()
    date             = models.DateField()
    description      = models.CharField(max_length=500)
    paid_by          = models.CharField(max_length=100)
    amount_original  = models.DecimalField(max_digits=12, decimal_places=2)
    currency_original = models.CharField(max_length=10, default="INR")
    amount_inr       = models.DecimalField(max_digits=12, decimal_places=2)
    split_type       = models.CharField(max_length=20)
    split_with       = models.JSONField(default=list)
    split_details    = models.JSONField(default=dict)
    notes            = models.TextField(blank=True)
    is_refund        = models.BooleanField(default=False)
    has_anomaly      = models.BooleanField(default=False)

    class Meta:
        app_label = "importer"
        ordering = ["date", "row_number"]

    def __str__(self):
        return f"{self.date} — {self.description} (₹{self.amount_inr})"


class ImportedSettlement(models.Model):
    """A row identified as a settlement during import."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session    = models.ForeignKey(ImportSession, on_delete=models.CASCADE, related_name="imported_settlements")
    row_number = models.IntegerField()
    date       = models.DateField()
    description = models.CharField(max_length=500)
    paid_by    = models.CharField(max_length=100)
    paid_to    = models.CharField(max_length=100, blank=True)
    amount_inr = models.DecimalField(max_digits=12, decimal_places=2)
    notes      = models.TextField(blank=True)

    class Meta:
        app_label = "importer"

    def __str__(self):
        return f"Settlement: {self.paid_by} → {self.paid_to} ₹{self.amount_inr}"
