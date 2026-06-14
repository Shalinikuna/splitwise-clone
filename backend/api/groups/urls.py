from django.urls import path
from . import views

urlpatterns = [
    path("", views.GroupListCreateView.as_view(), name="group-list-create"),
    path("<uuid:pk>/", views.GroupDetailView.as_view(), name="group-detail"),
    path("<uuid:pk>/invite/", views.invite_member, name="group-invite"),
    path("<uuid:pk>/members/<uuid:user_id>/", views.remove_member, name="group-remove-member"),
]
