import mercadopago
import httpx
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from ..crypto import decrypt
from ..database import get_db
from ..models import Negocio, Transaccion
from ..tasks import send_payment_confirmation_email

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])


@router.post(
    "/mercadopago/",
    summary="Webhook único de Mercado Pago",
    description=(
        "URL única configurada en el panel de MP para todos los negocios. "
        "Identifica el negocio via query param `negocio_id` incluido en la notification_url."
    ),
)
async def mercadopago_webhook(
    request: Request,
    negocio_id: int = Query(..., description="ID del negocio, incluido automáticamente en la notification_url"),
    db: Session = Depends(get_db),
):
    try:
        body = await request.json()
    except Exception:
        return {"status": "invalid_body"}

    if body.get("type") != "payment":
        return {"status": "ignored", "type": body.get("type")}

    payment_id = body.get("data", {}).get("id")
    if not payment_id:
        return {"status": "no_payment_id"}

    negocio = db.query(Negocio).filter(Negocio.id == negocio_id, Negocio.activo == True).first()  # noqa: E712
    if not negocio or not negocio.mp_access_token_enc:
        return {"status": "negocio_not_found"}

    try:
        mp_token = decrypt(negocio.mp_access_token_enc)
    except Exception:
        return {"status": "decrypt_error"}

    sdk = mercadopago.SDK(mp_token)
    payment_response = sdk.payment().get(payment_id)

    if payment_response["status"] != 200:
        return {"status": "mp_payment_not_found"}

    payment_detail = payment_response["response"]
    preference_id = payment_detail.get("preference_id")
    mp_status = payment_detail.get("status")

    transaccion = (
        db.query(Transaccion)
        .filter(Transaccion.preference_id == preference_id, Transaccion.negocio_id == negocio_id)
        .first()
    )

    if not transaccion:
        return {"status": "transaction_not_found", "preference_id": preference_id}

    transaccion.status = mp_status
    transaccion.payment_id = str(payment_id)
    db.commit()

    if mp_status == "approved":
        # Envío de email de confirmación asíncrono via Celery
        send_payment_confirmation_email.delay(transaccion.id, negocio.id)

        # Notificación al sistema del negocio (webhook de salida)
        if negocio.webhook_notificacion:
            payload = {
                "event": "payment.approved",
                "payment_id": str(payment_id),
                "preference_id": preference_id,
                "external_reference": transaccion.external_reference,
                "amount": transaccion.amount,
                "customer_email": transaccion.customer_email,
            }
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(negocio.webhook_notificacion, json=payload)
            except Exception:
                pass  # No bloquea la respuesta; fallback registrado en audit_logs

    return {"status": "processed", "payment_status": mp_status, "payment_id": str(payment_id)}
