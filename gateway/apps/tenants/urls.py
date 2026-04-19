from django.urls import path
from .views import NegocioListCreateView, NegocioDetailView

urlpatterns = [
    path('api/v1/negocios', NegocioListCreateView.as_view()),
    path('api/v1/negocios/<int:pk>', NegocioDetailView.as_view()),
]
