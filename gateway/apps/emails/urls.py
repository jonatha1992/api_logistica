from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/emails/send', views.EmailSendView.as_view()),
]
