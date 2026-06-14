from django.urls import path
from .views import comment_list_create

urlpatterns = [
    path("", comment_list_create, name="comment-list-create"),
]
