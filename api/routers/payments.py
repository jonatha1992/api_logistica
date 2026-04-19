import json
import os

import mercadopago
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware import get_tenant
from ..models import Negocio, Transaccion
from ..crypto import decrypt
from ..schemas import PaymentCreateRequest, PaymentCreateResponse

router = APIRouter(prefix="/api/v1/payments", tags=["Pagos"])


@router.post(
    "/create",
    response_model=PaymentCreateResponse,
    summary="Crear preferencia de pago",
    description="Genera un link de cobro en Mercado Pago usando las credenciales del negocio autenticado.",
)
def create_payment(
    data: PaymentCreateRequest,
    negocio: Negocio = Depends(get_tenant),
    db: Session = Depends(get_db),
):
    if not negocio.mp_access_token_enc:
        raise HTTPException(status_code=422, detail="El negocio no tiene configurado el token de Mercado Pago")

    try:
        mp_token = decrypt(negocio.mp_access_token_enc)
    except Exception:
        raise HTTPException(status_code=500, detail="Error al descifrar credenciales de Mercado Pago")

    sdk = mercadopago.SDK(mp_token)

    gateway_base = os.getenv("GATEWAY_WEBHOOK_BASE_URL", "https://tu-gateway.railway.app")
    notification_url = f"{gateway_base}/api/v1/webhooks/mercadopago/?negocio_id={negocio.id}"

    preference_payload = {
        "items": [
            {
                "title": data.description,
                "quantity": 1,
                "unit_price": float(data.amount),
                "currency_id": "ARS",
            }
        ],
        "payer": {"email": data.customer_email},
        "external_reference": data.external_reference or "",
        "notification_url": notification_url,
        "back_urls": {
            "success": data.back_url_success or "",
            "failure": data.back_url_failure or "",
            "pending": data.back_url_pending or "",
        },
    }

    preference_response = sdk.preference().create(preference_payload)

    if preference_response["status"] not in (200, 201):
        raise HTTPException(
            status_code=502,
            detail=f"Error de Mercado Pago: {preference_response.get('response', {})}",
        )

    preference = preference_response["response"]

    transaccion = Transaccion(
        negocio_id=negocio.id,
        preference_id=preference["id"],
        external_reference=data.external_reference,
        amount=data.amount,
        description=data.description,
        customer_email=data.customer_email,
        status="pending",
        init_point=preference["init_point"],
        metadata_json=json.dumps(data.metadata or {}),
    )
    db.add(transaccion)
    db.commit()
    db.refresh(transaccion)

    return PaymentCreateResponse(
        init_point=preference["init_point"],
        preference_id=preference["id"],
        external_reference=data.external_reference,
        status="pending",
    )
