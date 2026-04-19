# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

## Development Commands

All commands run from the `gateway/` directory.

```bash
# Run development server (uses SQLite + synchronous Celery automatically)
cd gateway && python manage.py runserver

# Run migrations
cd gateway && python manage.py migrate

# Run all tests
cd gateway && python manage.py test apps.tests

# Run a single test class or method
cd gateway && python manage.py test apps.tests.test_tenants.TenantAuthTest
cd gateway && python manage.py test apps.tests.test_tenants.TenantAuthTest.test_missing_auth_header

# Create default email templates for a Negocio
cd gateway && python manage.py crear_plantillas_default --negocio <id>
```

Settings module defaults to `gateway.settings.development` (set in `manage.py`). For production use `gateway.settings.production`.

## Architecture

This is a **Django 4.2 + DRF multi-tenant gateway** (v2.0.0). Each tenant is a `Negocio` object identified by a UUID API key.

### Request flow

1. `AuditLogMiddleware` — logs every authenticated request to `AuditLog` after response
2. `TenantMiddleware` — reads `Authorization: Bearer <api_key>`, looks up `Negocio`, injects `request.negocio`. Public routes (carrier queries, webhooks) bypass auth.
3. App views read `request.negocio` to scope data and load per-tenant credentials.

### Apps (`gateway/apps/`)

| App | Responsibility |
|---|---|
| `tenants` | `Negocio` model, middleware, API key auth, per-tenant throttling |
| `logistics` | Envia.com shipping quotes + carrier info (wraps `client_envia.py`) |
| `emails` | Jinja2 email templates per tenant, async send via Celery/Resend/SMTP |
| `payments` | MercadoPago preference creation, `Transaccion` model |
| `webhooks` | MercadoPago webhook receiver; fires `request.negocio.webhook_notificacion` |
| `audit` | `AuditLog` model + middleware; read via `/api/v1/audit/` |
| `panel` | Django template web panel at `/panel/` (no DRF) |

### Key design decisions

**Encrypted fields**: `EncryptedField` (in `apps/tenants/fields.py`) is a `TextField` subclass that transparently encrypts/decrypts with Fernet. Used for all sensitive tenant credentials: `mp_access_token`, `smtp_pass`, `resend_api_key`, `envia_token`, `whatsapp_api_key`. Requires `ENCRYPTION_KEY` env var — omitting it raises `RuntimeError` on first DB access.

**Per-tenant credentials**: Credentials for email, payments, and logistics are stored per `Negocio`. The global `ENVIA_TOKEN` / `ENVIA_API_URL` in settings is a fallback; if a `Negocio` has `envia_token` set, it takes priority.

**Celery in dev**: `development.py` sets `CELERY_TASK_ALWAYS_EAGER=True` so tasks run synchronously. Production requires a Redis broker.

### Environment variables

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret |
| `DATABASE_URL` | PostgreSQL DSN (omit to use SQLite in dev) |
| `REDIS_URL` | Celery broker (default: `redis://localhost:6379/0`) |
| `ENCRYPTION_KEY` | Fernet key for `EncryptedField` (base64, 32 bytes) |
| `ENVIRONMENT` | `TEST` or `PRO` — selects Envia.com endpoint |
| `TOKEN_TEST` / `TOKEN_PRO` | Envia.com API tokens |
| `ENVIA_API_URL_TEST` / `ENVIA_API_URL_PRO` | Envia.com base URLs |
| `GATEWAY_WEBHOOK_BASE_URL` | Public URL used as MercadoPago webhook callback |
| `ALLOWED_HOSTS` | Comma-separated hosts |

### API endpoints

All tenant-authenticated endpoints require `Authorization: Bearer <api_key>`.

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/` | public | Welcome |
| GET | `/api/v1/status` | public | Health check |
| GET | `/api/v1/config` | public | Active environment config |
| POST | `/api/v1/cotizar` | public | Quote shipping rates |
| GET | `/api/v1/carriers` | public | List Argentina carriers |
| GET | `/api/v1/carriers/<name>` | public | Carrier details |
| POST | `/api/v1/payments/create` | tenant | Create MercadoPago preference |
| POST | `/api/v1/webhooks/mercadopago/` | public | MercadoPago webhook |
| POST | `/api/v1/emails/send` | tenant | Send email via template |
| GET | `/api/v1/negocio/me` | tenant | Own Negocio info |
| GET/POST | `/api/v1/negocios` | superuser | List/create negocios |

Swagger UI: `/docs` · ReDoc: `/redoc`

### Testing

Tests live in `gateway/apps/tests/`. Each file sets `ENCRYPTION_KEY` via `os.environ` at the top to avoid `RuntimeError` during test setup. Use `APIClient` from DRF; set credentials with `self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {negocio.api_key}')`.
