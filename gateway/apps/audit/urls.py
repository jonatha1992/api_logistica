from django.urls import path
from .views import AuditLogListView

urlpatterns = [
    path('api/v1/audit', AuditLogListView.as_view()),
]
