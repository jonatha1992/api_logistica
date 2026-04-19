from django.urls import path
from . import views

app_name = 'panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.panel_login, name='login'),
    path('logout/', views.panel_logout, name='logout'),
    path('negocios/nuevo/', views.negocio_nuevo, name='negocio_nuevo'),
    path('negocios/<int:pk>/', views.negocio_editar, name='negocio_editar'),
    path('negocios/<int:pk>/toggle/', views.negocio_toggle, name='negocio_toggle'),
]
