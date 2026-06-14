from django.urls import path
from . import views

urlpatterns = [
    path("groups/<uuid:group_id>/expenses/", views.expense_list_create, name="expense-list-create"),
    path("expenses/<uuid:expense_id>/", views.expense_detail, name="expense-detail"),
    path("groups/<uuid:group_id>/balances/", views.group_balances, name="group-balances"),
]
