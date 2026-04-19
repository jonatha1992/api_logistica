from django.contrib import admin
from django.urls import path, include

admin.site.site_header = 'Gateway Maestro de Servicios'
admin.site.site_title = 'Gateway Admin'
admin.site.index_title = 'Panel de Administración Multi-Tenant'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.logistics.urls')),
    path('', include('apps.payments.urls')),
    path('', include('apps.webhooks.urls')),
    path('', include('apps.emails.urls')),
]
