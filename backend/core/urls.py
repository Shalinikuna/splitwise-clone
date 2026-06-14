from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("api.auth.urls")),
    path("api/groups/", include("api.groups.urls")),
    path("api/", include("api.expenses.urls")),
    path("api/", include("api.settlements.urls")),
    path("api/balances/", include("api.expenses.balance_urls")),
    path("api/expenses/<uuid:expense_id>/comments/", include("api.chat.urls")),
    path("api/import/", include("api.importer.urls")),
]
