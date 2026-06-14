from django.urls import path
from . import views

urlpatterns = [
    path("upload/",              views.upload_csv,     name="import-upload"),
    path("sessions/",            views.list_sessions,  name="import-sessions"),
    path("sessions/<uuid:session_id>/", views.session_report, name="import-session-report"),
]
