from datetime import datetime
from celery import shared_task
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, BaseLoader, select_autoescape

# Shared Jinja2 environment with HTML autoescaping — prevents XSS via user-supplied template data
_jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(['html', 'xml']),
)


def _send_via_resend(api_key: str, from_email: str, to_email: str, subject: str, html: str):
    import resend
    resend.api_key = api_key
    resend.Emails.send({
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": html,
    })


def _send_via_smtp(negocio, to_email: str, subject: str, html: str):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = negocio.smtp_from
    msg['To'] = to_email
    msg.attach(MIMEText(html, 'html'))

    with smtplib.SMTP(negocio.smtp_host, negocio.smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(negocio.smtp_user, negocio.smtp_pass)
        server.sendmail(negocio.smtp_from, [to_email], msg.as_string())


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_template_email(self, negocio_id: int, template_slug: str, to_email: str, data: dict):
    """
    Envía email usando plantilla Jinja2 del negocio.
    Usa Resend si hay resend_api_key configurado, sino fallback a SMTP.
    Reintenta hasta 3 veces con 60s de espera si falla.
    """
    from apps.tenants.models import Negocio
    from apps.emails.models import PlantillaEmail

    try:
        negocio = Negocio.objects.get(id=negocio_id)
        template = PlantillaEmail.objects.get(
            negocio=negocio, slug=template_slug, activa=True
        )

        # Brand context auto-inyectado — user data takes precedence
        brand_context = {
            'negocio_nombre': negocio.nombre_comercial or negocio.nombre,
            'negocio_slogan': negocio.slogan or '',
            'negocio_icono': negocio.icono_emoji or '📦',
            'negocio_color_primario': negocio.color_primario or '#4f46e5',
            'negocio_color_secundario': negocio.color_secundario or '#7c3aed',
            'negocio_logo_url': negocio.logo_url or '',
            'negocio_sitio_web': str(negocio.sitio_web) if negocio.sitio_web else '#',
            'negocio_email_soporte': negocio.email_soporte or negocio.smtp_from or '',
            'negocio_texto_footer': negocio.texto_footer or (negocio.nombre_comercial or negocio.nombre),
            'current_year': datetime.now().year,
        }
        context = {**brand_context, **data}

        # Use autoescaped environment to prevent HTML injection via user-supplied fields
        rendered_subject = _jinja_env.from_string(template.asunto).render(**context)
        rendered_body = _jinja_env.from_string(template.cuerpo_html).render(**context)

        if negocio.resend_api_key:
            if not negocio.smtp_from:
                raise ValueError(
                    f'Negocio {negocio_id}: se requiere smtp_from (email remitente) para enviar via Resend.'
                )
            _send_via_resend(negocio.resend_api_key, negocio.smtp_from, to_email, rendered_subject, rendered_body)
            provider = 'resend'
        else:
            _send_via_smtp(negocio, to_email, rendered_subject, rendered_body)
            provider = 'smtp'

        return {'status': 'sent', 'to': to_email, 'template': template_slug, 'provider': provider}

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
