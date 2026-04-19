# api_logistica/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

# ===============================================================================
# MODELOS PARA LA INTERFAZ DE NUESTRA PROPIA API (Lo que nuestros usuarios nos envían)
# ===============================================================================

class SimpleAddress(BaseModel):
    street: str = Field(..., example="Av. Constitucion")
    number: str = Field(..., example="405")
    city: str = Field(..., example="Monterrey")
    state: str = Field(..., example="NL", description="Código de estado de 2 letras.")
    postal_code: str = Field(..., example="64000")
    country_code: str = Field(..., example="MX", description="Código de país de 2 letras.")
    contact_name: str = Field(..., example="Jane Doe")
    contact_email: str = Field(..., example="jane.doe@example.com")
    contact_phone: str = Field(..., example="8181818181")

class SimpleParcel(BaseModel):
    weight: float = Field(..., example=1, description="Peso en kg")
    height: float = Field(..., example=10, description="Altura en cm")
    width: float = Field(..., example=20, description="Ancho en cm")
    length: float = Field(..., example=20, description="Largo en cm")
    content: str = Field(..., example="Zapatos")

class QuoteRequest(BaseModel):
    origin: SimpleAddress
    destination: SimpleAddress
    parcels: List[SimpleParcel]
    carrier: Optional[str] = Field(None, example="fedex", description="Transportista específico a cotizar.")
    currency: str = Field("MXN", example="MXN", description="Moneda para la cotización.")

# ===============================================================================
# MODELOS PARA EL CLIENTE DE ENVIA.COM (Lo que enviamos a su API)
# ===============================================================================

class EnviaAddress(BaseModel):
    name: str
    company: Optional[str] = None
    email: str
    phone: str
    street: str
    number: str
    district: str
    city: str
    state: str
    country: str
    postalCode: str
    reference: Optional[str] = ""

class EnviaDimensions(BaseModel):
    length: float
    width: float
    height: float

class EnviaParcel(BaseModel):
    content: str
    amount: int = 1
    type: str = "box"
    weight: float
    insurance: int = 0
    declaredValue: int = 0
    weightUnit: str = "KG"
    lengthUnit: str = "CM"
    dimensions: EnviaDimensions

class EnviaShipment(BaseModel):
    carrier: str
    type: int = 0

class EnviaSettings(BaseModel):
    currency: str

class EnviaQuotePayload(BaseModel):
    origin: EnviaAddress
    destination: EnviaAddress
    packages: List[EnviaParcel]
    shipment: EnviaShipment
    settings: EnviaSettings

# ===============================================================================
# MODELOS PARA ENDPOINTS ADICIONALES (Carriers, Config, etc.)
# ===============================================================================

class CarrierInfo(BaseModel):
    id: Optional[int] = Field(None, description="ID único del carrier")
    name: str = Field(..., example="oca", description="Nombre del carrier")
    carrier_code: Optional[str] = Field(None, example="OCA_AR", description="Código del carrier")
    description: Optional[str] = Field(None, example="OCA Argentina", description="Descripción del carrier")
    active: Optional[bool] = Field(None, description="Si el carrier está activo")
    country: Optional[str] = Field(None, example="AR", description="Código de país")
    category: Optional[str] = Field(None, example="local", description="Categoría del carrier (local, internacional, postal)")

class CarrierListResponse(BaseModel):
    meta: str = Field(..., example="carriers", description="Tipo de respuesta")
    total: int = Field(..., example=8, description="Total de carriers disponibles")
    data: List[CarrierInfo] = Field(..., description="Lista de carriers")

class ConfigInfo(BaseModel):
    environment: str = Field(..., example="PRO", description="Entorno actual (TEST/PRO)")
    api_url: str = Field(..., example="https://api.envia.com", description="URL base de la API")
    token_configured: bool = Field(..., description="Si el token está configurado")
    available_environments: List[str] = Field(["TEST", "PRO"], description="Entornos disponibles")

class HealthResponse(BaseModel):
    status: str = Field(..., example="operativo", description="Estado del servicio")
    environment: str = Field(..., example="PRO", description="Entorno actual")
    timestamp: str = Field(..., description="Timestamp de la respuesta")


# ===============================================================================
# MODELOS PARA EL GATEWAY MULTI-TENANT
# ===============================================================================

class PaymentCreateRequest(BaseModel):
    amount: float = Field(..., example=1500.00, description="Monto a cobrar")
    description: str = Field(..., example="Suscripción Mensual Pro", description="Descripción del cobro")
    customer_email: str = Field(..., example="usuario@ejemplo.com", description="Email del pagador")
    external_reference: Optional[str] = Field(None, example="PEDIDO-9921", description="Referencia interna del negocio")
    metadata: Optional[dict] = Field(None, example={"plan": "anual", "user_id": 45})
    back_url_success: Optional[str] = Field(None, description="URL de redirección en pago exitoso")
    back_url_failure: Optional[str] = Field(None, description="URL de redirección en pago fallido")
    back_url_pending: Optional[str] = Field(None, description="URL de redirección en pago pendiente")


class PaymentCreateResponse(BaseModel):
    init_point: str = Field(..., description="URL de la pasarela de pago de Mercado Pago")
    preference_id: str = Field(..., description="ID de la preferencia creada en MP")
    external_reference: Optional[str] = Field(None, description="Referencia interna del negocio")
    status: str = Field(..., example="pending", description="Estado inicial de la transacción")


class EmailSendRequest(BaseModel):
    template_slug: str = Field(..., example="recupero-clave", description="Identificador de la plantilla")
    to: str = Field(..., example="destinatario@mail.com", description="Dirección de destino")
    data: Optional[dict] = Field(
        None,
        example={"nombre": "Carlos", "link": "https://negocio.com/reset/xyz"},
        description="Variables para reemplazar en la plantilla ({{ variable }})",
    )


class EmailSendResponse(BaseModel):
    status: str = Field(..., example="queued", description="Estado del envío (queued / sent / error)")
    message: str = Field(..., description="Descripción del resultado")
