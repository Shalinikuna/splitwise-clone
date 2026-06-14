from django.urls import path
from .views import my_overall_balances

urlpatterns = [
    path("", my_overall_balances, name="my-overall-balances"),
]
