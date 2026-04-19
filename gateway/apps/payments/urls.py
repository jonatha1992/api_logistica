from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/payments/create', views.CreatePaymentView.as_view()),
]
