import os
os.environ.setdefault('ENCRYPTION_KEY', '7qe05Kv1VC3A0H8v09NCMdUjp7VHMjSGLpoAVNkMfWo=')

from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIClient
from apps.tenants.models import Negocio
from apps.emails.models import PlantillaEmail


class EmailSendTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.negocio = Negocio.objects.create(
            nombre='Negocio Email',
            smtp_host='smtp.test.com',
            smtp_port=587,
            smtp_user='user@test.com',
            smtp_pass='password123',
            smtp_from='noreply@test.com',
        )
        self.plantilla = PlantillaEmail.objects.create(
            negocio=self.negocio,
            slug='bienvenida',
            asunto='Bienvenido {{ nombre }}',
            cuerpo_html='<h1>Hola {{ nombre }}</h1>',
            activa=True,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.negocio.api_key}')

    def test_email_template_not_found(self):
        r = self.client.post('/api/v1/emails/send', {
            'template_slug': 'slug-inexistente',
            'to': 'test@test.com',
        }, format='json')
        self.assertEqual(r.status_code, 404)

    @patch('apps.emails.tasks.send_template_email.delay')
    def test_email_queued_successfully(self, mock_delay):
        r = self.client.post('/api/v1/emails/send', {
            'template_slug': 'bienvenida',
            'to': 'destinatario@test.com',
            'data': {'nombre': 'Carlos'},
        }, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['status'], 'queued')
        mock_delay.assert_called_once()

    def test_negocio_sin_smtp_ni_resend_returns_422(self):
        negocio2 = Negocio.objects.create(nombre='Sin proveedor')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {negocio2.api_key}')
        r = self.client.post('/api/v1/emails/send', {
            'template_slug': 'bienvenida',
            'to': 'test@test.com',
        }, format='json')
        self.assertEqual(r.status_code, 422)

    @patch('apps.emails.tasks.send_template_email.delay')
    def test_resend_only_negocio_puede_enviar(self, mock_delay):
        """Negocio con solo resend_api_key (sin SMTP) debe pasar el gate."""
        negocio_resend = Negocio.objects.create(
            nombre='Solo Resend',
            resend_api_key='re_test_fake_key',
            smtp_from='noreply@mitienda.com',
        )
        PlantillaEmail.objects.create(
            negocio=negocio_resend,
            slug='bienvenida',
            asunto='Bienvenido',
            cuerpo_html='<h1>Hola</h1>',
            activa=True,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {negocio_resend.api_key}')
        r = self.client.post('/api/v1/emails/send', {
            'template_slug': 'bienvenida',
            'to': 'cliente@test.com',
        }, format='json')
        self.assertEqual(r.status_code, 200)
        mock_delay.assert_called_once()


class BrandContextTest(TestCase):
    """Verifica que brand_context se inyecta correctamente al renderizar templates."""

    def setUp(self):
        from apps.emails.models import PlantillaEmail
        self.negocio = Negocio.objects.create(
            nombre='NombreInterno',
            nombre_comercial='Mi Tienda',
            slogan='Lo mejor de lo mejor',
            icono_emoji='🛒',
            color_primario='#FF6B35',
            smtp_from='noreply@mitienda.com',
            smtp_host='smtp.test.com',
            smtp_user='user@test.com',
            smtp_pass='pass',
        )
        self.plantilla = PlantillaEmail.objects.create(
            negocio=self.negocio,
            slug='test-brand',
            asunto='Email de {{ negocio_nombre }}',
            cuerpo_html='<p>{{ negocio_nombre }} - {{ negocio_icono }} - {{ current_year }}</p>',
            activa=True,
        )

    @patch('apps.emails.tasks._send_via_smtp')
    def test_brand_context_inyectado(self, mock_smtp):
        """current_year, negocio_nombre e icono deben aparecer en el email renderizado."""
        from apps.emails.tasks import send_template_email
        send_template_email(self.negocio.id, 'test-brand', 'dest@test.com', {})

        mock_smtp.assert_called_once()
        _negocio_arg, to_arg, subject_arg, html_arg = mock_smtp.call_args[0]
        from datetime import datetime
        year = str(datetime.now().year)
        self.assertIn('Mi Tienda', subject_arg)
        self.assertIn('Mi Tienda', html_arg)
        self.assertIn('🛒', html_arg)
        self.assertIn(year, html_arg)

    @patch('apps.emails.tasks._send_via_smtp')
    def test_autoescape_bloquea_html_injection(self, mock_smtp):
        """Campos de usuario con HTML no deben inyectarse sin escapar."""
        from apps.emails.models import PlantillaEmail
        PlantillaEmail.objects.create(
            negocio=self.negocio,
            slug='test-escape',
            asunto='Test',
            cuerpo_html='<p>{{ mensaje }}</p>',
            activa=True,
        )
        from apps.emails.tasks import send_template_email
        send_template_email(
            self.negocio.id, 'test-escape', 'dest@test.com',
            {'mensaje': '<img src=x onerror=alert(1)>'}
        )
        mock_smtp.assert_called_once()
        _n, _to, _subj, html_arg = mock_smtp.call_args[0]
        self.assertNotIn('<img', html_arg)
        self.assertIn('&lt;img', html_arg)
