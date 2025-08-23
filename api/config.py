# api_logistica/config.py
import os
from dotenv import load_dotenv

# Carga las variables del archivo .env en las variables de entorno del sistema
load_dotenv()

# Configuración de entorno (TEST o PRO)
ENVIRONMENT = os.getenv("ENVIRONMENT", "TEST").upper()

# Lee las variables de entorno según el entorno
if ENVIRONMENT == "TEST":
    ENVIA_API_URL = os.getenv("ENVIA_API_URL_TEST", "https://ship-test.envia.com")
    TOKEN = os.getenv("TOKEN_TEST")
else:
    ENVIA_API_URL = os.getenv("ENVIA_API_URL_PRO", "https://api.envia.com")
    TOKEN = os.getenv("TOKEN_PRO")

# Headers para la autenticación
API_HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

# Información de configuración actual
CONFIG_INFO = {
    "environment": ENVIRONMENT,
    "api_url": ENVIA_API_URL,
    "token_configured": bool(TOKEN),
}
