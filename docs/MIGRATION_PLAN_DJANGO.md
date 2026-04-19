# Plan de Migración: FastAPI → Django + Admin Interface

**Versión**: 1.0  
**Fecha**: 2026-04-18  
**Estado**: Listo para ejecución  
**Repo**: jonatha1992/api_logistica

---

## Contexto del proyecto actual

Sistema de logística y gateway de pagos multi-tenant construido en FastAPI.  
Se migra a Django para obtener Django Admin — interfaz visual para cargar credenciales de cada negocio (tokens de Mercado Pago, SMTP, plantillas de email) sin tocar código.

### Tecnologías actuales (FastAPI)
- FastAPI 0.116 + Uvicorn
- SQLAlchemy 2.0 + psycopg2 (PostgreSQL)
- Celery + Redis (tareas async)
- Mercado Pago SDK
- Fernet encryption (cryptography)
- Jinja2 templates
- slowapi rate limiting

### Tecnologías objetivo (Django)
- Django 4.2 LTS + Gunicorn
- Django ORM + psycopg2 (PostgreSQL)
- Django REST Framework 3.15
- Celery + Redis + django-celery-results
- Django Admin (interfaz de credenciales)
- DRF Throttling (rate limiting nativo)
- Fernet encryption (mismo mecanismo)

---

## Endpoints actuales a preservar (compatibilidad total)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Bienvenida + info de versión |
| GET | `/api/v1/status` | Health check |
| POST | `/api/v1/cotizar` | Cotizar envíos Envia.com |
| GET | `/api/v1/carriers` | Listar carriers Argentina |
| GET | `/api/v1/carriers/{name}` | Info de carrier específico |
| GET | `/api/v1/config` | Configuración actual |
| POST | `/api/v1/payments/create` | Crear pago Mercado Pago (**multi-tenant**) |
| POST | `/api/v1/webhooks/mercadopago/` | Webhook único MP (**multi-tenant**) |
| POST | `/api/v1/emails/send` | Enviar email con plantilla (**multi-tenant**) |

### Autenticación multi-tenant
Todas las rutas marcadas `multi-tenant` requieren:
```
Authorization: Bearer <API_KEY_DEL_NEGOCIO>
```
El sistema busca el `Negocio` en DB por esa key e inyecta sus credenciales.

---

## Modelos de base de datos actuales (SQLAlchemy → Django ORM)

### Negocio
```
id, nombre, api_key (unique),
mp_access_token_enc (Fernet encrypted),
webhook_notificacion,
smtp_host, smtp_port, smtp_user, smtp_pass_enc (Fernet encrypted), smtp_from,
activo, created_at
```

### Transaccion
```
id, negocio_id (FK),
preference_id (unique), payment_id, external_reference,
amount, description, customer_email,
status (pending|approved|rejected|cancelled|in_process),
init_point, metadata_json,
created_at, updated_at
```

### PlantillaEmail
```
id, negocio_id (FK),
slug (ej: "recupero-clave", "pago-confirmado"),
asunto (soporta {{ variables }}),
cuerpo_html (soporta {{ variables }}),
activa, created_at
```

### AuditLog
```
id, negocio_id (FK nullable),
endpoint, method, status_code, error_message,
created_at
```

---

## Estructura de carpetas objetivo

```
gateway/
├── gateway/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
│
├── apps/
│   ├── tenants/          ← Negocio, API keys, EncryptedField, TenantMiddleware
│   ├── payments/         ← Transaccion, /api/v1/payments/create
│   ├── emails/           ← PlantillaEmail, /api/v1/emails/send, tasks Celery
│   ├── webhooks/         ← /api/v1/webhooks/mercadopago/
│   ├── logistics/        ← /cotizar, /carriers (reutiliza client_envia.py y services.py)
│   └── audit/            ← AuditLog, AuditLogMiddleware
│
├── requirements.txt
├── Dockerfile
├── manage.py
└── .env
```

---

## Fases de implementación

---

### FASE 0 — Preparación

**Objetivo**: Entorno limpio, sin tocar producción.

**Tareas**:
- [ ] Crear branch `feature/django-migration` desde `main`
- [ ] Crear carpeta `gateway/` en la raíz del repo
- [ ] Ejecutar `django-admin startproject gateway gateway/`
- [ ] Documentar todas las variables de entorno actuales

**Variables de entorno a preservar sin cambios**:
```bash
ENVIRONMENT=TEST|PRO
TOKEN_TEST=...
TOKEN_PRO=...
ENVIA_API_URL_TEST=https://ship-test.envia.com
ENVIA_API_URL_PRO=https://api.envia.com
DATABASE_URL=postgresql://...
ENCRYPTION_KEY=...
REDIS_URL=redis://localhost:6379/0
GATEWAY_WEBHOOK_BASE_URL=https://tu-gateway.railway.app
```

**Entregable**: Branch creado, proyecto Django inicializado, `.env` documentado.

---

### FASE 1 — Proyecto Django base

**Objetivo**: Django corriendo con settings por ambiente.

**requirements.txt objetivo**:
```
django==4.2.16
djangorestframework==3.15.2
psycopg2-binary==2.9.10
django-environ==0.11.2
cryptography==44.0.0
celery==5.4.0
redis==5.2.1
django-celery-results==2.5.1
django-celery-beat==2.6.0
mercadopago==2.2.2
httpx==0.28.1
requests==2.32.5
jinja2==3.1.4
gunicorn==22.0.0
```

**settings/base.py — puntos clave**:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_celery_results',
    'django_celery_beat',
    'apps.tenants',
    'apps.payments',
    'apps.emails',
    'apps.webhooks',
    'apps.logistics',
    'apps.audit',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
}

CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Argentina/Buenos_Aires'
```

**Comando de verificación**:
```bash
python manage.py check
python manage.py runserver
# → /admin debe cargar sin errores
```

**Entregable**: `manage.py runserver` levanta, `/admin` accesible.

---

### FASE 2 — Modelos y migraciones

**Objetivo**: Esquema completo en Django ORM con campo encriptado custom.

**Campo encriptado (apps/tenants/fields.py)**:
```python
from cryptography.fernet import Fernet
from django.db import models
import os

class EncryptedField(models.TextField):
    """
    Encripta automáticamente al guardar en DB.
    Desencripta automáticamente al leer.
    Nunca persiste valores en plain text.
    """
    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        f = Fernet(os.environ['ENCRYPTION_KEY'].encode())
        return f.decrypt(value.encode()).decode()

    def get_prep_value(self, value):
        if not value:
            return value
        f = Fernet(os.environ['ENCRYPTION_KEY'].encode())
        return f.encrypt(value.encode()).decode()
```

**Mapa de tipos SQLAlchemy → Django**:

| SQLAlchemy | Django ORM |
|---|---|
| `Column(String(200), nullable=False)` | `CharField(max_length=200)` |
| `Column(String(200), nullable=True)` | `CharField(max_length=200, blank=True, null=True)` |
| `Column(Text, nullable=True)` | `TextField(blank=True, null=True)` |
| `Column(Float, nullable=False)` | `FloatField()` |
| `Column(Boolean, default=True)` | `BooleanField(default=True)` |
| `Column(Integer, default=587)` | `IntegerField(default=587)` |
| `Column(DateTime, default=utcnow)` | `DateTimeField(auto_now_add=True)` |
| `Column(DateTime, onupdate=utcnow)` | `DateTimeField(auto_now=True)` |
| `Column(String(64), unique=True)` | `CharField(max_length=64, unique=True, db_index=True)` |
| `ForeignKey("negocios.id")` | `ForeignKey('tenants.Negocio', on_delete=models.CASCADE)` |
| `Column(Text, nullable=True)` + _enc suffix | `EncryptedField(blank=True, null=True)` |

**Modelo Negocio (apps/tenants/models.py)**:
```python
import uuid
from django.db import models
from .fields import EncryptedField

class Negocio(models.Model):
    nombre = models.CharField(max_length=200)
    api_key = models.CharField(max_length=64, unique=True, db_index=True, editable=False)
    mp_access_token = EncryptedField(blank=True, null=True)
    webhook_notificacion = models.URLField(max_length=500, blank=True, null=True)
    smtp_host = models.CharField(max_length=200, blank=True, null=True)
    smtp_port = models.IntegerField(default=587)
    smtp_user = models.CharField(max_length=200, blank=True, null=True)
    smtp_pass = EncryptedField(blank=True, null=True)
    smtp_from = models.EmailField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = uuid.uuid4().hex  # genera API key automáticamente
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Negocio'
        verbose_name_plural = 'Negocios'
```

**Comandos**:
```bash
python manage.py makemigrations tenants payments emails audit
python manage.py migrate
python manage.py showmigrations  # todo debe estar en [X]
```

**Entregable**: Todas las tablas creadas, migraciones en verde.

---

### FASE 3 — Django Admin (interfaz de credenciales)

**Objetivo**: Panel visual para crear/editar negocios con credenciales encriptadas.  
**Este es el valor principal del cambio a Django.**

**apps/tenants/admin.py**:
```python
from django.contrib import admin
from django.utils.html import format_html
from .models import Negocio

@admin.register(Negocio)
class NegocioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'api_key_preview', 'mp_configurado', 'smtp_configurado', 'activo', 'created_at']
    list_filter = ['activo', 'created_at']
    readonly_fields = ['api_key', 'created_at']
    search_fields = ['nombre']
    actions = ['activar_negocios', 'desactivar_negocios']

    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'activo', 'api_key')
        }),
        ('Mercado Pago', {
            'fields': ('mp_access_token', 'webhook_notificacion'),
            'classes': ('collapse',),
            'description': 'El token se encripta automáticamente al guardar. Nunca se muestra en plain text.'
        }),
        ('Configuración SMTP', {
            'fields': ('smtp_host', 'smtp_port', 'smtp_user', 'smtp_pass', 'smtp_from'),
            'classes': ('collapse',),
            'description': 'Credenciales SMTP del negocio. La contraseña se encripta automáticamente.'
        }),
    )

    def api_key_preview(self, obj):
        return f"{obj.api_key[:8]}..."
    api_key_preview.short_description = 'API Key'

    def mp_configurado(self, obj):
        return bool(obj.mp_access_token)
    mp_configurado.boolean = True
    mp_configurado.short_description = 'MP'

    def smtp_configurado(self, obj):
        return bool(obj.smtp_host)
    smtp_configurado.boolean = True
    smtp_configurado.short_description = 'SMTP'

    def activar_negocios(self, request, queryset):
        queryset.update(activo=True)
    def desactivar_negocios(self, request, queryset):
        queryset.update(activo=False)
```

**apps/emails/admin.py**:
```python
@admin.register(PlantillaEmail)
class PlantillaEmailAdmin(admin.ModelAdmin):
    list_display = ['negocio', 'slug', 'asunto_preview', 'activa', 'created_at']
    list_filter = ['negocio', 'activa']
    search_fields = ['slug', 'asunto']

    # Nota: considerar django-ckeditor o similar para editar HTML
    # en producción para mejor UX en el campo cuerpo_html
```

**apps/payments/admin.py**:
```python
@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ['negocio', 'external_reference', 'amount', 'status', 'customer_email', 'created_at']
    list_filter = ['status', 'negocio', 'created_at']
    search_fields = ['external_reference', 'customer_email', 'payment_id', 'preference_id']
    date_hierarchy = 'created_at'
    readonly_fields = [f.name for f in Transaccion._meta.get_fields()
                       if hasattr(f, 'name')]  # todo solo lectura
```

**apps/audit/admin.py**:
```python
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['negocio', 'endpoint', 'method', 'status_code', 'created_at']
    list_filter = ['negocio', 'method', 'status_code']
    date_hierarchy = 'created_at'
    readonly_fields = ['negocio', 'endpoint', 'method', 'status_code', 'error_message', 'created_at']
```

**Entregable**: 
- `/admin` permite crear negocios con credenciales encriptadas
- Ver transacciones filtradas por estado
- Ver logs de auditoría por negocio y fecha

---

### FASE 4 — Middleware multi-tenant

**Objetivo**: Equivalente al `get_tenant()` de FastAPI, pero como Django Middleware.

**apps/tenants/middleware.py**:
```python
from django.http import JsonResponse
from .models import Negocio

class TenantMiddleware:
    RUTAS_PUBLICAS = {
        '/',
        '/api/v1/status',
        '/api/v1/config',
        '/api/v1/carriers',
        '/api/v1/cotizar',
    }
    PREFIJOS_PUBLICOS = ('/admin/', '/api/v1/webhooks/mercadopago/')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.negocio = None

        if self._es_publica(request.path):
            return self.get_response(request)

        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return JsonResponse(
                {'detail': 'Header requerido: Authorization: Bearer <API_KEY>'},
                status=401
            )

        api_key = auth.removeprefix('Bearer ').strip()
        try:
            request.negocio = Negocio.objects.get(api_key=api_key, activo=True)
        except Negocio.DoesNotExist:
            return JsonResponse({'detail': 'API key inválida o negocio inactivo'}, status=401)

        return self.get_response(request)

    def _es_publica(self, path):
        if path in self.RUTAS_PUBLICAS:
            return True
        return any(path.startswith(p) for p in self.PREFIJOS_PUBLICOS)
```

**Orden en settings/base.py**:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'apps.audit.middleware.AuditLogMiddleware',    # 1. registra después de la respuesta
    'apps.tenants.middleware.TenantMiddleware',    # 2. inyecta request.negocio
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
```

**Entregable**: Rutas protegidas rechazan requests sin API key válida con 401.

---

### FASE 5 — Módulo de Logística (migración directa)

**Objetivo**: Los 4 endpoints de Envia.com funcionando en Django, sin cambios en la lógica de negocio.

**Estrategia**: Copiar `client_envia.py` y `services.py` del proyecto FastAPI. Solo cambiar las excepciones de `HTTPException` → excepciones propias + respuestas DRF.

**apps/logistics/exceptions.py**:
```python
class EnviaAPIError(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
```

**apps/logistics/views.py**:
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import client_envia, services
from .serializers import QuoteRequestSerializer

class CotizarView(APIView):
    def post(self, request):
        ser = QuoteRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            rates = client_envia.get_rates_dict(ser.validated_data)
            return Response(rates)
        except EnviaAPIError as e:
            return Response({'detail': e.detail}, status=e.status_code)

class CarriersView(APIView):
    def get(self, request):
        carriers = services.get_carriers_from_envia()
        return Response({'meta': 'carriers', 'total': len(carriers), 'data': carriers})

class CarrierDetailView(APIView):
    def get(self, request, carrier_name):
        carrier = services.get_carrier_by_name(carrier_name)
        if not carrier:
            return Response({'detail': f"Carrier '{carrier_name}' no encontrado"}, status=404)
        return Response(carrier)

class StatusView(APIView):
    def get(self, request):
        from datetime import datetime
        import config
        return Response({
            'status': 'operativo',
            'environment': config.ENVIRONMENT,
            'timestamp': datetime.now().isoformat()
        })

class ConfigView(APIView):
    def get(self, request):
        return Response(services.get_config_info())
```

**apps/logistics/urls.py**:
```python
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
```

**Entregable**: Los 10 tests actuales pasan adaptados a `APIClient` de DRF.

---

### FASE 6 — Módulo de Pagos

**Objetivo**: `POST /api/v1/payments/create` funcionando con credenciales del tenant.

**apps/payments/serializers.py**:
```python
from rest_framework import serializers

class PaymentCreateSerializer(serializers.Serializer):
    amount = serializers.FloatField(min_value=0.01)
    description = serializers.CharField(max_length=500)
    customer_email = serializers.EmailField()
    external_reference = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.DictField(required=False)
    back_url_success = serializers.URLField(required=False)
    back_url_failure = serializers.URLField(required=False)
    back_url_pending = serializers.URLField(required=False)
```

**apps/payments/views.py**:
```python
import json, os
import mercadopago
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Transaccion
from .serializers import PaymentCreateSerializer
from apps.tenants.crypto import decrypt

class CreatePaymentView(APIView):
    def post(self, request):
        negocio = request.negocio  # inyectado por TenantMiddleware

        if not negocio.mp_access_token:
            return Response({'detail': 'Negocio sin token de Mercado Pago configurado'}, status=422)

        ser = PaymentCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        sdk = mercadopago.SDK(negocio.mp_access_token)  # EncryptedField desencripta al leer

        gateway_base = os.environ.get('GATEWAY_WEBHOOK_BASE_URL', '')
        notification_url = f"{gateway_base}/api/v1/webhooks/mercadopago/?negocio_id={negocio.id}"

        preference_payload = {
            "items": [{"title": data['description'], "quantity": 1, "unit_price": float(data['amount'])}],
            "payer": {"email": data['customer_email']},
            "external_reference": data.get('external_reference', ''),
            "notification_url": notification_url,
            "back_urls": {
                "success": data.get('back_url_success', ''),
                "failure": data.get('back_url_failure', ''),
                "pending": data.get('back_url_pending', ''),
            },
        }

        response = sdk.preference().create(preference_payload)
        if response['status'] not in (200, 201):
            return Response({'detail': f"Error MP: {response.get('response', {})}"}, status=502)

        preference = response['response']

        transaccion = Transaccion.objects.create(
            negocio=negocio,
            preference_id=preference['id'],
            external_reference=data.get('external_reference'),
            amount=data['amount'],
            description=data['description'],
            customer_email=data['customer_email'],
            status='pending',
            init_point=preference['init_point'],
            metadata_json=json.dumps(data.get('metadata') or {}),
        )

        return Response({
            'init_point': preference['init_point'],
            'preference_id': preference['id'],
            'external_reference': transaccion.external_reference,
            'status': 'pending',
        }, status=201)
```

**Entregable**: Payment flow completo: create → webhook → email de confirmación.

---

### FASE 7 — Módulo de Emails + Celery

**Objetivo**: Envío asíncrono de emails con plantillas Jinja2 por negocio.

**gateway/celery.py**:
```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway.settings.production')

app = Celery('gateway')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**apps/emails/tasks.py**:
```python
from celery import shared_task
from jinja2 import Template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_template_email(self, negocio_id: int, template_slug: str, to_email: str, data: dict):
    """
    Envía email usando plantilla y SMTP del negocio.
    Reintenta 3 veces con 60s de espera si falla.
    """
    from apps.tenants.models import Negocio
    from apps.emails.models import PlantillaEmail

    try:
        negocio = Negocio.objects.get(id=negocio_id)
        template = PlantillaEmail.objects.get(
            negocio=negocio, slug=template_slug, activa=True
        )

        rendered_subject = Template(template.asunto).render(**data)
        rendered_body = Template(template.cuerpo_html).render(**data)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = rendered_subject
        msg['From'] = negocio.smtp_from
        msg['To'] = to_email
        msg.attach(MIMEText(rendered_body, 'html'))

        # negocio.smtp_pass desencripta automáticamente por EncryptedField
        with smtplib.SMTP(negocio.smtp_host, negocio.smtp_port) as server:
            server.starttls()
            server.login(negocio.smtp_user, negocio.smtp_pass)
            server.sendmail(negocio.smtp_from, [to_email], msg.as_string())

        return {'status': 'sent', 'to': to_email}

    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_payment_confirmation_email(self, transaccion_id: int, negocio_id: int):
    """Disparado automáticamente cuando MP aprueba un pago."""
    from apps.payments.models import Transaccion
    try:
        t = Transaccion.objects.get(id=transaccion_id)
        if not t.customer_email:
            return {'status': 'skipped'}
        send_template_email.delay(
            negocio_id=negocio_id,
            template_slug='pago-confirmado',
            to_email=t.customer_email,
            data={
                'amount': t.amount,
                'description': t.description,
                'external_reference': t.external_reference,
                'customer_email': t.customer_email,
                'payment_id': t.payment_id,
            }
        )
        return {'status': 'queued'}
    except Exception as exc:
        raise self.retry(exc=exc)
```

**apps/emails/views.py**:
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import PlantillaEmail
from .serializers import EmailSendSerializer
from .tasks import send_template_email

class EmailSendView(APIView):
    throttle_classes = [PerNegocioThrottle]  # ver Fase 9

    def post(self, request):
        negocio = request.negocio

        if not negocio.smtp_host:
            return Response({'detail': 'Negocio sin SMTP configurado'}, status=422)

        ser = EmailSendSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        if not PlantillaEmail.objects.filter(
            negocio=negocio, slug=data['template_slug'], activa=True
        ).exists():
            return Response(
                {'detail': f"Plantilla '{data['template_slug']}' no encontrada"},
                status=404
            )

        send_template_email.delay(
            negocio_id=negocio.id,
            template_slug=data['template_slug'],
            to_email=data['to'],
            data=data.get('data') or {},
        )

        return Response({'status': 'queued', 'message': f"Correo a {data['to']} encolado"})
```

**Iniciar worker**:
```bash
celery -A gateway worker --loglevel=info
```

**Entregable**: Correos se envían asincrónicamente con reintentos automáticos.

---

### FASE 8 — Webhook + Auditoría

**Objetivo**: Webhook único de MP y registro de todas las interacciones.

**apps/webhooks/views.py**:
```python
import mercadopago
import httpx
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.tenants.models import Negocio
from apps.payments.models import Transaccion
from apps.emails.tasks import send_payment_confirmation_email

class MercadoPagoWebhookView(APIView):
    def post(self, request):
        negocio_id = request.GET.get('negocio_id')
        if not negocio_id:
            return Response({'status': 'missing_negocio_id'}, status=400)

        body = request.data
        if body.get('type') != 'payment':
            return Response({'status': 'ignored'})

        payment_id = body.get('data', {}).get('id')
        if not payment_id:
            return Response({'status': 'no_payment_id'})

        try:
            negocio = Negocio.objects.get(id=negocio_id, activo=True)
        except Negocio.DoesNotExist:
            return Response({'status': 'negocio_not_found'}, status=404)

        if not negocio.mp_access_token:
            return Response({'status': 'no_mp_token'}, status=422)

        sdk = mercadopago.SDK(negocio.mp_access_token)
        payment_response = sdk.payment().get(payment_id)

        if payment_response['status'] != 200:
            return Response({'status': 'mp_error'}, status=502)

        detail = payment_response['response']
        preference_id = detail.get('preference_id')
        mp_status = detail.get('status')

        try:
            t = Transaccion.objects.get(preference_id=preference_id, negocio=negocio)
        except Transaccion.DoesNotExist:
            return Response({'status': 'transaction_not_found'})

        t.status = mp_status
        t.payment_id = str(payment_id)
        t.save()

        if mp_status == 'approved':
            send_payment_confirmation_email.delay(t.id, negocio.id)

            if negocio.webhook_notificacion:
                try:
                    import httpx
                    httpx.post(negocio.webhook_notificacion, json={
                        'event': 'payment.approved',
                        'payment_id': str(payment_id),
                        'external_reference': t.external_reference,
                        'amount': t.amount,
                        'customer_email': t.customer_email,
                    }, timeout=5.0)
                except Exception:
                    pass

        return Response({'status': 'processed', 'payment_status': mp_status})
```

**apps/audit/middleware.py**:
```python
from .models import AuditLog

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        negocio = getattr(request, 'negocio', None)
        if negocio:
            try:
                AuditLog.objects.create(
                    negocio=negocio,
                    endpoint=request.path,
                    method=request.method,
                    status_code=response.status_code,
                )
            except Exception:
                pass
        return response
```

**Entregable**: Webhook procesa pagos, cada interacción queda en `AuditLog`.

---

### FASE 9 — Rate Limiting

**Objetivo**: Máximo 30 emails/minuto por negocio.

**Throttle por negocio (no por IP)**:
```python
# apps/emails/throttles.py
from rest_framework.throttling import SimpleRateThrottle

class PerNegocioThrottle(SimpleRateThrottle):
    rate = '30/minute'
    scope = 'negocio_email'

    def get_cache_key(self, request, view):
        negocio = getattr(request, 'negocio', None)
        if negocio:
            return f'throttle_negocio_{negocio.id}'
        return self.get_ident(request)
```

**En settings/base.py**:
```python
REST_FRAMEWORK = {
    ...
    'DEFAULT_THROTTLE_RATES': {
        'negocio_email': '30/minute',
    }
}
```

**Entregable**: Request 31 del mismo negocio en 60s devuelve HTTP 429.

---

### FASE 10 — Tests

**Objetivo**: Cobertura completa del gateway.

**Migrar tests existentes**:
```python
# Antes (FastAPI)
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.get('/api/v1/status')

# Después (Django + DRF)
from rest_framework.test import APITestCase, APIClient

class StatusTestCase(APITestCase):
    def test_get_status(self):
        response = self.client.get('/api/v1/status')
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.data)
```

**Tests nuevos requeridos**:
```
test_tenant_invalid_api_key           → 401
test_tenant_inactive_negocio          → 401
test_create_payment_no_mp_token       → 422
test_create_payment_success           → 201 + preference_id
test_webhook_approves_transaction     → status=approved
test_webhook_unknown_negocio          → 404
test_email_template_not_found         → 404
test_email_queued_successfully        → 200 queued
test_email_rate_limit_exceeded        → 429
test_audit_log_created_on_request     → AuditLog count +1
test_encrypted_field_not_plain_text   → DB value != raw token
```

**Comandos**:
```bash
python manage.py test
# o con pytest-django
pytest --ds=gateway.settings.development -v
```

**Entregable**: Suite completa pasa, incluyendo tests de encriptación.

---

### FASE 11 — Deploy en Railway

**Objetivo**: Dockerfile Django funcionando en Railway con variables de entorno.

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=gateway.settings.production

RUN apt-get update && apt-get install -y gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/status')"

CMD python manage.py migrate --noinput && \
    gunicorn gateway.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2
```

**railway.json**:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "healthcheckPath": "/api/v1/status",
    "healthcheckTimeout": 30
  }
}
```

**Variables de entorno en Railway**:
```bash
DJANGO_SETTINGS_MODULE=gateway.settings.production
SECRET_KEY=<django-insecure-reemplazar-con-valor-seguro>
DEBUG=False
ALLOWED_HOSTS=*.railway.app,tu-dominio.com
DATABASE_URL=postgresql://...
ENCRYPTION_KEY=<mismo-fernet-key-del-proyecto-actual>
REDIS_URL=redis://...
GATEWAY_WEBHOOK_BASE_URL=https://tu-gateway.railway.app
ENVIRONMENT=PRO
TOKEN_PRO=<envia-token>
```

**Entregable**: Deploy exitoso, `/admin` y `/api/v1/status` accesibles en HTTPS.

---

## Resumen de fases y dependencias

```
FASE 0 (Preparación)
    ↓
FASE 1 (Django base)
    ↓
FASE 2 (Modelos + migraciones)
    ↓
FASE 3 (Django Admin ← valor principal)
    ↓
FASE 4 (Middleware multi-tenant)
    ↓
    ├── FASE 5 (Logística)
    ├── FASE 6 (Pagos)
    └── FASE 7 (Emails + Celery)
            ↓
        FASE 8 (Webhook + Auditoría)
            ↓
        FASE 9 (Rate Limiting)
            ↓
        FASE 10 (Tests)
            ↓
        FASE 11 (Deploy)
```

| Fase | Descripción | Prioridad | Riesgo |
|------|-------------|-----------|--------|
| 0 | Preparación + branching | Crítica | Bajo |
| 1 | Proyecto Django base | Crítica | Bajo |
| 2 | Modelos + migraciones | Crítica | Medio |
| **3** | **Django Admin (credenciales)** | **Alta** | **Bajo** |
| 4 | Middleware multi-tenant | Crítica | Medio |
| 5 | Módulo Logística | Alta | Bajo |
| 6 | Módulo Pagos | Alta | Medio |
| 7 | Emails + Celery | Alta | Medio |
| 8 | Webhook + Auditoría | Media | Bajo |
| 9 | Rate Limiting | Media | Bajo |
| 10 | Tests completos | Alta | Bajo |
| 11 | Deploy Railway | Crítica | Bajo |

---

## Archivos a reutilizar del proyecto FastAPI

Estos archivos se copian con cambios mínimos:

| Archivo FastAPI | Destino Django | Cambios requeridos |
|---|---|---|
| `api/client_envia.py` | `apps/logistics/client_envia.py` | `HTTPException` → `EnviaAPIError` |
| `api/services.py` | `apps/logistics/services.py` | `HTTPException` → excepciones propias |
| `api/config.py` | `gateway/settings/base.py` | Variables incorporadas a Django settings |
| `api/crypto.py` | `apps/tenants/fields.py` | Lógica dentro de `EncryptedField` |
| `api/email_sender.py` | `apps/emails/tasks.py` | Inline en la task de Celery |
| `api/tasks.py` | `apps/emails/tasks.py` | `@shared_task` en vez de `@celery_app.task` |

---

## Notas importantes para el modelo ejecutor

1. **`EncryptedField` es el componente más crítico** — todos los tests de seguridad dependen de que la encriptación funcione correctamente antes de avanzar a otras fases.

2. **Las URLs deben ser idénticas** — hay sistemas externos (MP webhook, posibles integraciones) que apuntan a estas URLs. No cambiar paths.

3. **El `ENCRYPTION_KEY` debe ser el mismo** — si la DB ya tiene datos encriptados, usar la misma key del proyecto FastAPI. Si es DB nueva, generar una con `Fernet.generate_key()`.

4. **Middleware order importa** — `AuditLogMiddleware` debe ir antes que `TenantMiddleware` en la lista para ejecutarse después (stacking inverso de Django).

5. **Celery worker es un proceso separado** — en Railway se necesita un segundo servicio o Procfile con `celery -A gateway worker`.

6. **`manage.py migrate` en startup** — el Dockerfile incluye `migrate --noinput` antes de arrancar Gunicorn para que las migraciones corran automáticamente en cada deploy.
