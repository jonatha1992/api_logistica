"""
Tareas asíncronas con Celery + Redis.
Equivalente a django-celery-email para el stack FastAPI.

Iniciar el worker:
    celery -A api.tasks worker --loglevel=info
"""
import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "gateway",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Argentina/Buenos_Aires",
    enable_utc=True,
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_template_email(self, negocio_id: int, template_slug: str, to_email: str, data: dict):
    """
    Envía un correo usando la plantilla y credenciales SMTP del negocio.
    Reintenta hasta 3 veces con 60 s de espera si falla.
    """
    from .database import SessionLocal
    from .models import Negocio, PlantillaEmail
    from .crypto import decrypt
    from .email_sender import send_email
    from jinja2 import Template

    db = SessionLocal()
    try:
        negocio = db.query(Negocio).filter(Negocio.id == negocio_id).first()
        template = (
            db.query(PlantillaEmail)
            .filter(
                PlantillaEmail.negocio_id == negocio_id,
                PlantillaEmail.slug == template_slug,
                PlantillaEmail.activa == True,  # noqa: E712
            )
            .first()
        )

        if not negocio or not template:
            return {"status": "skipped", "reason": "negocio o plantilla no encontrada"}

        rendered_subject = Template(template.asunto).render(**data)
        rendered_body = Template(template.cuerpo_html).render(**data)

        smtp_pass = decrypt(negocio.smtp_pass_enc) if negocio.smtp_pass_enc else ""

        send_email(
            smtp_host=negocio.smtp_host,
            smtp_port=negocio.smtp_port,
            smtp_user=negocio.smtp_user,
            smtp_pass=smtp_pass,
            from_email=negocio.smtp_from,
            to_email=to_email,
            subject=rendered_subject,
            body_html=rendered_body,
        )

        return {"status": "sent", "to": to_email, "template": template_slug}

    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_payment_confirmation_email(self, transaccion_id: int, negocio_id: int):
    """
    Disparado automáticamente por el webhook cuando un pago es aprobado.
    Usa la plantilla con slug 'pago-confirmado' del negocio correspondiente.
    """
    from .database import SessionLocal
    from .models import Transaccion

    db = SessionLocal()
    try:
        transaccion = db.query(Transaccion).filter(Transaccion.id == transaccion_id).first()
        if not transaccion or not transaccion.customer_email:
            return {"status": "skipped", "reason": "transaccion sin email de cliente"}

        send_template_email.delay(
            negocio_id=negocio_id,
            template_slug="pago-confirmado",
            to_email=transaccion.customer_email,
            data={
                "amount": transaccion.amount,
                "description": transaccion.description,
                "external_reference": transaccion.external_reference,
                "customer_email": transaccion.customer_email,
                "payment_id": transaccion.payment_id,
            },
        )

        return {"status": "queued", "transaccion_id": transaccion_id}

    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        db.close()
