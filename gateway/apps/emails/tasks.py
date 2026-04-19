from celery import shared_task
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_template_email(self, negocio_id: int, template_slug: str, to_email: str, data: dict):
    """
    Envía email usando la plantilla y credenciales SMTP del negocio.
    Reintenta hasta 3 veces con 60s de espera si falla.
    """
    from apps.tenants.models import Negocio
    from apps.emails.models import PlantillaEmail

    try:
        negocio = Negocio.objects.get(id=negocio_id)
        template = PlantillaEmail.objects.get(
            negocio=negocio, slug=template_slug, activa=True
        )

        rendered_subject = Template(template.asunto).render(**data)
        rendered_body = Template(template.cuerpo_html).render(**data)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = rendered_subject
        msg['From'] = negocio.smtp_from
        msg['To'] = to_email
        msg.attach(MIMEText(rendered_body, 'html'))

        # smtp_pass se desencripta automáticamente por EncryptedField
        with smtplib.SMTP(negocio.smtp_host, negocio.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(negocio.smtp_user, negocio.smtp_pass)
            server.sendmail(negocio.smtp_from, [to_email], msg.as_string())

        return {'status': 'sent', 'to': to_email, 'template': template_slug}

    except (Negocio.DoesNotExist, PlantillaEmail.DoesNotExist) as e:
        return {'status': 'skipped', 'reason': str(e)}
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_payment_confirmation_email(self, transaccion_id: int, negocio_id: int):
    """
    Disparado automáticamente por el webhook cuando MP aprueba un pago.
    Usa la plantilla 'pago-confirmado' del negocio.
    """
    from apps.payments.models import Transaccion

    try:
        t = Transaccion.objects.get(id=transaccion_id)
        if not t.customer_email:
            return {'status': 'skipped', 'reason': 'sin customer_email'}

        send_template_email.delay(
            negocio_id=negocio_id,
            template_slug='pago-confirmado',
            to_email=t.customer_email,
            data={
                'amount': t.amount,
                'description': t.description,
                'external_reference': t.external_reference,
                'customer_email': t.customer_email,
                'payment_id': t.payment_id,
            }
        )
        return {'status': 'queued', 'transaccion_id': transaccion_id}

    except Exception as exc:
        raise self.retry(exc=exc)
