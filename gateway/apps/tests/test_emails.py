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

    def test_negocio_sin_smtp_returns_422(self):
        negocio2 = Negocio.objects.create(nombre='Sin SMTP')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {negocio2.api_key}')
        r = self.client.post('/api/v1/emails/send', {
            'template_slug': 'bienvenida',
            'to': 'test@test.com',
        }, format='json')
        self.assertEqual(r.status_code, 422)
