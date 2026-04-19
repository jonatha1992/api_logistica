from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/webhooks/mercadopago/', views.MercadoPagoWebhookView.as_view()),
]
