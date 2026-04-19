# api_logistica/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# ── Envia.com ────────────────────────────────────────────────────────────────
ENVIRONMENT = os.getenv("ENVIRONMENT", "TEST").upper()

if ENVIRONMENT == "TEST":
    ENVIA_API_URL = os.getenv("ENVIA_API_URL_TEST", "https://ship-test.envia.com")
    TOKEN = os.getenv("TOKEN_TEST")
else:
    ENVIA_API_URL = os.getenv("ENVIA_API_URL_PRO", "https://api.envia.com")
    TOKEN = os.getenv("TOKEN_PRO")

API_HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

CONFIG_INFO = {
    "environment": ENVIRONMENT,
    "api_url": ENVIA_API_URL,
    "token_configured": bool(TOKEN),
}

# ── Gateway multi-tenant ─────────────────────────────────────────────────────
# DATABASE_URL      → postgresql://user:pass@host:5432/gateway_db
# ENCRYPTION_KEY    → Fernet key (generar con: python -c "from api.crypto import generate_key; print(generate_key())")
# REDIS_URL         → redis://localhost:6379/0
# GATEWAY_WEBHOOK_BASE_URL → URL pública del gateway (ej: https://tu-gateway.railway.app)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/gateway_db")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
GATEWAY_WEBHOOK_BASE_URL = os.getenv("GATEWAY_WEBHOOK_BASE_URL", "https://tu-gateway.railway.app")
