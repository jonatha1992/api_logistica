# Estructura del Proyecto

```
api_logistica/
├── .venv/                          # Entorno virtual
├── gateway/                        # Django - Servicio único (migrado de FastAPI)
│   ├── manage.py
│   ├── requirements.txt            # Dependencias del servicio
│   ├── apps/
│   │   ├── tenants/                # Multi-tenancy: Negocio + api_key + EncryptedField
│   │   │   ├── models.py           # Negocio (mp_access_token, smtp_pass cifrados)
│   │   │   ├── fields.py           # EncryptedField (auto-cifra/descifra)
│   │   │   ├── middleware.py       # TenantMiddleware (autenticación por API Key)
│   │   │   ├── throttles.py        # PerNegocioThrottle (rate limiting)
│   │   │   ├── serializers.py      # NegocioCreateSerializer, NegocioResponseSerializer
│   │   │   ├── views.py            # CRUD: GET/POST /api/v1/negocios, PATCH/DELETE /api/v1/negocios/<id>
│   │   │   └── urls.py
│   │   │
│   │   ├── logistics/              # Cotizaciones y carriers (integración Envia.com)
│   │   │   ├── client_envia.py     # Cliente HTTP para Envia.com
│   │   │   ├── services.py         # get_carriers_from_envia(), get_config_info()
│   │   │   ├── exceptions.py       # EnviaAPIError
│   │   │   ├── serializers.py      # Request + Response serializers
│   │   │   ├── views.py            # Welcome, Status, Cotizar, Carriers, Config
│   │   │   └── urls.py             # GET / | /api/v1/status | /cotizar | /carriers | /config
│   │   │
│   │   ├── payments/               # Pagos con MercadoPago
│   │   │   ├── models.py           # Transaccion
│   │   │   ├── serializers.py      # PaymentCreateSerializer, PaymentCreateResponseSerializer
│   │   │   ├── views.py            # POST /api/v1/payments/create
│   │   │   └── urls.py
│   │   │
│   │   ├── webhooks/               # Webhooks entrantes de MercadoPago
│   │   │   ├── views.py            # POST /api/v1/webhooks/mercadopago/
│   │   │   └── urls.py
│   │   │
│   │   ├── emails/                 # Envío de emails con Jinja2 + Celery
│   │   │   ├── models.py           # PlantillaEmail (slug, asunto, cuerpo_html)
│   │   │   ├── serializers.py      # EmailSendSerializer, EmailSendResponseSerializer
│   │   │   ├── views.py            # POST /api/v1/emails/send
│   │   │   ├── tasks.py            # Celery: send_template_email, send_payment_confirmation_email
│   │   │   └── urls.py
│   │   │
│   │   ├── audit/                  # Auditoría automática de requests
│   │   │   ├── models.py           # AuditLog
│   │   │   ├── middleware.py       # AuditLogMiddleware (auto-registra cada request)
│   │   │   ├── views.py            # GET /api/v1/audit (con filtros)
│   │   │   └── urls.py
│   │   │
│   │   └── tests/                  # Tests del gateway
│   │
│   └── gateway/                    # Configuración Django
│       ├── settings/
│       │   ├── base.py             # Settings compartidos
│       │   ├── development.py      # SQLite local
│       │   └── production.py       # PostgreSQL + Railway
│       ├── celery.py
│       ├── urls.py                 # Rutas raíz + Swagger /docs + /redoc
│       └── wsgi.py
│
├── scripts/                        # Utilidades y diagnóstico
├── tests/                          # Tests FastAPI (legacy, a migrar a gateway/apps/tests/)
├── docs/
│   ├── structure.md                # Este archivo
│   ├── planning.md
│   └── tech.md
├── .gitignore
├── .dockerignore
├── Dockerfile                      # Docker único (build context = raíz)
├── railway.json                    # Deploy en Railway
└── CLAUDE.md
```

## Endpoints disponibles

| Método | Endpoint | App | Auth |
|--------|----------|-----|------|
| GET | `/` | logistics | No |
| GET | `/api/v1/status` | logistics | No |
| POST | `/api/v1/cotizar` | logistics | API Key |
| GET | `/api/v1/carriers` | logistics | API Key |
| GET | `/api/v1/carriers/<name>` | logistics | API Key |
| GET | `/api/v1/config` | logistics | No |
| POST | `/api/v1/payments/create` | payments | API Key |
| POST | `/api/v1/webhooks/mercadopago/` | webhooks | No |
| POST | `/api/v1/emails/send` | emails | API Key |
| GET/POST | `/api/v1/negocios` | tenants | No* |
| GET/PATCH/DELETE | `/api/v1/negocios/<id>` | tenants | No* |
| GET | `/api/v1/audit` | audit | No* |
| GET | `/docs/` | — | No |
| GET | `/redoc/` | — | No |
| GET | `/admin/` | — | Django admin |

*Proteger con autenticación Django Admin en producción.

## Correr en desarrollo

```bash
# Django
python gateway/manage.py runserver

# Celery worker
celery -A gateway worker --loglevel=info

# Celery beat (tareas programadas)
celery -A gateway beat --loglevel=info
```

## Deploy en Railway

Variables de entorno requeridas:
```bash
ENVIRONMENT=PRO
TOKEN_PRO=<token_envia>
SECRET_KEY=<django_secret_key>
DATABASE_URL=<postgresql_url>
REDIS_URL=<redis_url>
ENCRYPTION_KEY=<fernet_key>
GATEWAY_WEBHOOK_BASE_URL=https://tu-app.railway.app
```
```
