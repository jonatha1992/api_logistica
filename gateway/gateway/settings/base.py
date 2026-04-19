from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / '.env')

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-development-only')
DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'drf_spectacular',
    'django_celery_results',
    'django_celery_beat',
]

LOCAL_APPS = [
    'apps.tenants',
    'apps.payments',
    'apps.emails',
    'apps.webhooks',
    'apps.logistics',
    'apps.audit',
    'apps.panel',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'apps.audit.middleware.AuditLogMiddleware',
    'apps.tenants.middleware.TenantMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gateway.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gateway.wsgi.application'

import dj_database_url
db_url = os.environ.get('DATABASE_URL')
if db_url:
    DATABASES = {
        'default': dj_database_url.parse(db_url, conn_max_age=600)
    }
    DATABASES['default'].setdefault('OPTIONS', {}).update({'options': '-c search_path=public'})
else:
    # Fallback: PostgreSQL placeholder; development.py overrides this with SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'OPTIONS': {'options': '-c search_path=public'},
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Django REST Framework ─────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_RATES': {
        'negocio_email': '30/minute',
    },
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'API de Logística - Gateway Maestro de Servicios',
    'DESCRIPTION': (
        'Gateway central para cotizaciones de envíos, pagos con MercadoPago, '
        'webhooks y envío de emails. Multi-tenant con autenticación por API Key.'
    ),
    'VERSION': '2.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CONTACT': {'name': 'Soporte', 'email': 'tecnofusion.it@gmail.com'},
}

# ── Celery ────────────────────────────────────────────────────────────────────
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Argentina/Buenos_Aires'
CELERY_ENABLE_UTC = True

# ── Encryption ────────────────────────────────────────────────────────────────
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', '')

# ── Envia.com ────────────────────────────────────────────────────────────────
ENVIA_ENVIRONMENT = os.environ.get('ENVIRONMENT', 'TEST').upper()
if ENVIA_ENVIRONMENT == 'TEST':
    ENVIA_API_URL = os.environ.get('ENVIA_API_URL_TEST', 'https://ship-test.envia.com')
    ENVIA_TOKEN = os.environ.get('TOKEN_TEST', '')
else:
    ENVIA_API_URL = os.environ.get('ENVIA_API_URL_PRO', 'https://api.envia.com')
    ENVIA_TOKEN = os.environ.get('TOKEN_PRO', '')

ENVIA_API_HEADERS = {
    'Authorization': f'Bearer {ENVIA_TOKEN}',
    'Content-Type': 'application/json',
}

# ── Gateway ───────────────────────────────────────────────────────────────────
GATEWAY_WEBHOOK_BASE_URL = os.environ.get('GATEWAY_WEBHOOK_BASE_URL', 'https://tu-gateway.railway.app')
