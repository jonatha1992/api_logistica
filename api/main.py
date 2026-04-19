# api_logistica/main.py
from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from datetime import datetime
from typing import List, Optional
from .schemas import QuoteRequest, CarrierInfo, CarrierListResponse, ConfigInfo, HealthResponse
from . import client_envia, services, config
from .database import create_tables
from .middleware import audit_log_middleware, set_tenant_state_middleware
from .routers import payments, webhooks, emails

# Configuración mejorada de FastAPI con documentación completa
app = FastAPI(
    title="API de Logística - Gateway Maestro de Servicios",
    version="2.0.0",
    description="""
    ## Gateway Maestro de Servicios Multi-Tenant

    Sistema centralizado de **Pagos, Correos y Logística** para múltiples negocios.

    ### Módulos disponibles

    * **Logística** — Cotizar envíos con OCA, Andreani, DHL, FedEx y más
    * **Pagos** — Generar links de cobro con Mercado Pago por negocio
    * **Correos** — Enviar emails con plantillas dinámicas por negocio
    * **Webhooks** — Recibir notificaciones de MP y reenviarlas al sistema origen

    ### Autenticación (endpoints multi-tenant)
    Incluir el header: `Authorization: Bearer <API_KEY_DEL_NEGOCIO>`

    ### Entornos Envia.com
    La API soporta entornos de **TEST** y **PRODUCCIÓN**.
    """,
    contact={
        "name": "API de Logística",
        "url": "https://github.com/tu-repositorio",
    },
    license_info={
        "name": "MIT",
    },
)

# ── Rate limiting global ─────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Middlewares HTTP (ejecutan en orden de definición: primero = más externo) ─
app.middleware("http")(audit_log_middleware)       # registra en audit_logs después de cada respuesta
app.middleware("http")(set_tenant_state_middleware)  # resuelve API key → Negocio en request.state

# ── Routers del Gateway multi-tenant ────────────────────────────────────────
app.include_router(payments.router)
app.include_router(webhooks.router)
app.include_router(emails.router)

# ── Startup: crear tablas si no existen ─────────────────────────────────────
@app.on_event("startup")
def startup_event():
    try:
        create_tables()
    except Exception:
        pass  # No bloquea si la DB no está disponible en este entorno


# ============================================================================
# ENDPOINTS PRINCIPALES
# ============================================================================

@app.get(
    "/", 
    tags=["Información General"],
    summary="Página de inicio",
    description="Mensaje de bienvenida a la API"
)
def read_root():
    """Endpoint de bienvenida con información básica de la API."""
    return {
        "mensaje": "Bienvenido a la API de Logística",
        "version": "1.0.0",
        "docs": "/docs",
        "environment": config.ENVIRONMENT
    }

@app.get(
    "/api/v1/status", 
    tags=["Información General"],
    response_model=HealthResponse,
    summary="Estado del servicio",
    description="Verifica el estado del servicio y la configuración actual"
)
def get_status():
    """
    Endpoint de health check que retorna el estado del servicio.
    
    - **status**: Estado operativo del servicio
    - **environment**: Entorno actual (TEST/PRO)  
    - **timestamp**: Fecha y hora de la consulta
    """
    return HealthResponse(
        status="operativo",
        environment=config.ENVIRONMENT,
        timestamp=datetime.now().isoformat()
    )

@app.post(
    "/api/v1/cotizar", 
    tags=["Cotizaciones"],
    summary="Cotizar envío",
    description="Obtiene cotizaciones de envío utilizando los servicios de Envia.com"
)
def post_cotizacion(datos_cotizacion: QuoteRequest):
    """
    Realiza una cotización de envío con los datos proporcionados.
    
    - **origin**: Dirección de origen completa
    - **destination**: Dirección de destino completa  
    - **parcels**: Lista de paquetes a enviar
    - **carrier**: Transportista específico (opcional)
    - **currency**: Moneda para la cotización
    
    Retorna información detallada de precios, tiempos de entrega y servicios disponibles.
    """
    rates = client_envia.get_rates(datos_cotizacion)
    return rates

# ============================================================================
# ENDPOINTS DE CARRIERS
# ============================================================================

@app.get(
    "/api/v1/carriers",
    tags=["Carriers"],
    response_model=CarrierListResponse,
    summary="Listar carriers",
    description="Obtiene la lista completa de transportistas disponibles en Argentina"
)
def get_carriers():
    """
    Obtiene todos los carriers (transportistas) disponibles en Argentina.
    
    La respuesta incluye:
    - **ID único** de cada carrier
    - **Nombre** del transportista
    - **Categoría** (local, internacional, postal)
    - **Estado** (activo/inactivo)
    
    Los carriers se categorizan automáticamente:
    - **Locales**: OCA, Andreani, Urbano, Rueddo
    - **Internacionales**: DHL, FedEx  
    - **Postales**: Correo Argentino
    - **Otros**: DPD, etc.
    """
    try:
        carriers = services.get_carriers_from_envia()
        
        return CarrierListResponse(
            meta="carriers",
            total=len(carriers),
            data=carriers
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al obtener carriers: {str(e)}"
        )

@app.get(
    "/api/v1/carriers/{carrier_name}",
    tags=["Carriers"],
    response_model=CarrierInfo,
    summary="Información de carrier",
    description="Obtiene información detallada de un transportista específico"
)
def get_carrier_info(
    carrier_name: str = Path(
        ..., 
        description="Nombre del carrier", 
        example="oca"
    )
):
    """
    Obtiene información detallada de un carrier específico.
    
    - **carrier_name**: Nombre del transportista (ej: "oca", "andreani", "dhl")
    
    Retorna información completa del carrier incluyendo ID, categoría y estado.
    """
    try:
        carrier = services.get_carrier_by_name(carrier_name)
        
        if not carrier:
            raise HTTPException(
                status_code=404,
                detail=f"Carrier '{carrier_name}' no encontrado. Carriers disponibles: oca, andreani, dhl, fedex, correoArgentino, urbano, rueddo, dpd"
            )
        
        return carrier
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al obtener información del carrier: {str(e)}"
        )

# ============================================================================
# ENDPOINTS DE CONFIGURACIÓN
# ============================================================================

@app.get(
    "/api/v1/config",
    tags=["Configuración"],
    response_model=ConfigInfo,
    summary="Configuración actual",
    description="Muestra la configuración actual de la API"
)
def get_config():
    """
    Obtiene información sobre la configuración actual de la API.
    
    Incluye:
    - **Entorno** actual (TEST/PRO)
    - **URL base** de la API de Envia.com
    - **Estado del token** (configurado o no)
    - **Entornos disponibles**
    
    Útil para verificar qué configuración está activa.
    """
    try:
        return services.get_config_info()
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener configuración: {str(e)}"
        )
