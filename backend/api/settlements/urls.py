from django.urls import path
from .views import settlement_list_create

urlpatterns = [
    path("groups/<uuid:group_id>/settlements/", settlement_list_create, name="settlement-list-create"),
]
