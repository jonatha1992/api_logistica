from django.urls import path
from . import views

urlpatterns = [
    path('', views.WelcomeView.as_view()),
    path('api/v1/status', views.StatusView.as_view()),
    path('api/v1/cotizar', views.CotizarView.as_view()),
    path('api/v1/carriers', views.CarriersView.as_view()),
    path('api/v1/carriers/<str:carrier_name>', views.CarrierDetailView.as_view()),
    path('api/v1/config', views.ConfigView.as_view()),
]
