from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware import get_tenant
from ..models import Negocio, PlantillaEmail
from ..schemas import EmailSendRequest, EmailSendResponse
from ..tasks import send_template_email

router = APIRouter(prefix="/api/v1/emails", tags=["Correos"])

# Rate limit por negocio (API key) para no saturar el sistema SMTP compartido
limiter = Limiter(key_func=lambda request: request.headers.get("Authorization", get_remote_address(request)))


@router.post(
    "/send",
    response_model=EmailSendResponse,
    summary="Enviar correo con plantilla",
    description=(
        "Envía un correo usando la plantilla identificada por `template_slug` "
        "y las credenciales SMTP del negocio autenticado. "
        "El envío es asíncrono (Celery). Límite: 30 correos/minuto por negocio."
    ),
)
@limiter.limit("30/minute")
def send_email_endpoint(
    request: Request,
    data: EmailSendRequest,
    negocio: Negocio = Depends(get_tenant),
    db: Session = Depends(get_db),
):
    if not negocio.smtp_host:
        raise HTTPException(status_code=422, detail="El negocio no tiene configurado el servidor SMTP")

    template = (
        db.query(PlantillaEmail)
        .filter(
            PlantillaEmail.negocio_id == negocio.id,
            PlantillaEmail.slug == data.template_slug,
            PlantillaEmail.activa == True,  # noqa: E712
        )
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Plantilla '{data.template_slug}' no encontrada para este negocio",
        )

    send_template_email.delay(
        negocio_id=negocio.id,
        template_slug=data.template_slug,
        to_email=data.to,
        data=data.data or {},
    )

    return EmailSendResponse(
        status="queued",
        message=f"Correo a {data.to} encolado para envío asíncrono",
    )
