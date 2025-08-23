# api_logistica/main.py
from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import List, Optional
from .schemas import QuoteRequest, CarrierInfo, CarrierListResponse, ConfigInfo, HealthResponse
from . import client_envia, services, config

# Configuración mejorada de FastAPI con documentación completa
app = FastAPI(
    title="API de Logística - Integración Envia.com",
    version="1.0.0",
    description="""
    ## API de Logística para Argentina
    
    Esta API permite:
    
    * **Cotizar envíos** con múltiples transportistas
    * **Consultar carriers** disponibles en Argentina
    * **Obtener información** de configuración
    
    ### Carriers Disponibles
    
    - **Locales**: OCA, Andreani, Urbano, Rueddo
    - **Internacionales**: DHL, FedEx
    - **Postales**: Correo Argentino
    - **Otros**: DPD
    
    ### Entornos
    
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
