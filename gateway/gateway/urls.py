from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

admin.site.site_header = 'Gateway Maestro de Servicios'
admin.site.site_title = 'Gateway Admin'
admin.site.index_title = 'Panel de Administración Multi-Tenant'

urlpatterns = [
    path('', RedirectView.as_view(url='/panel/login/', permanent=False)),
    path('admin/', admin.site.urls),

    # OpenAPI / Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Panel de gestión (web)
    path('panel/', include('apps.panel.urls')),

    # Apps
    path('', include('apps.logistics.urls')),
    path('', include('apps.payments.urls')),
    path('', include('apps.webhooks.urls')),
    path('', include('apps.emails.urls')),
    path('', include('apps.tenants.urls')),
    path('', include('apps.audit.urls')),
]
