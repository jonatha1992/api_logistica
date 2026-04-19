from django.urls import path
from .views import NegocioListCreateView, NegocioDetailView, NegocioMeView

urlpatterns = [
    path('api/v1/negocio/me', NegocioMeView.as_view()),
    path('api/v1/negocios', NegocioListCreateView.as_view()),
    path('api/v1/negocios/<int:pk>', NegocioDetailView.as_view()),
]
