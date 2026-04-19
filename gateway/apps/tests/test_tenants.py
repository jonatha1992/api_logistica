import os
os.environ.setdefault('ENCRYPTION_KEY', '7qe05Kv1VC3A0H8v09NCMdUjp7VHMjSGLpoAVNkMfWo=')

from django.test import TestCase
from rest_framework.test import APIClient
from apps.tenants.models import Negocio


class TenantAuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.negocio = Negocio.objects.create(
            nombre='Negocio Test',
            smtp_host='smtp.test.com',
        )

    def test_missing_auth_header(self):
        r = self.client.post('/api/v1/payments/create', {}, format='json')
        self.assertEqual(r.status_code, 401)
        import json
        body = json.loads(r.content)
        self.assertIn('detail', body)

    def test_invalid_api_key(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer key-invalida-xyz')
        r = self.client.post('/api/v1/payments/create', {}, format='json')
        self.assertEqual(r.status_code, 401)

    def test_valid_api_key_passes_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.negocio.api_key}')
        # La request fallará por validación de payload, pero ya pasó auth (no 401)
        r = self.client.post('/api/v1/payments/create', {}, format='json')
        self.assertNotEqual(r.status_code, 401)

    def test_inactive_negocio_rejected(self):
        self.negocio.activo = False
        self.negocio.save()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.negocio.api_key}')
        r = self.client.post('/api/v1/payments/create', {}, format='json')
        self.assertEqual(r.status_code, 401)

    def test_public_routes_no_auth_required(self):
        for path in ['/', '/api/v1/status', '/api/v1/config']:
            r = self.client.get(path)
            self.assertNotEqual(r.status_code, 401, f"Ruta pública {path} exige auth erróneamente")


class EncryptedFieldTest(TestCase):
    def test_token_encrypted_in_db(self):
        negocio = Negocio.objects.create(
            nombre='Test Encriptación',
            mp_access_token='TEST_TOKEN_SECRETO_12345',
        )
        # Leer directo de DB (sin ORM, sin desencriptación)
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT mp_access_token FROM tenants_negocio WHERE id = %s",
                [negocio.id]
            )
            raw = cursor.fetchone()[0]
        # El valor en DB NO debe ser el token original
        self.assertNotEqual(raw, 'TEST_TOKEN_SECRETO_12345')
        self.assertIsNotNone(raw)
        # El valor leído via ORM SÍ debe ser el token original
        negocio.refresh_from_db()
        self.assertEqual(negocio.mp_access_token, 'TEST_TOKEN_SECRETO_12345')

    def test_api_key_auto_generated(self):
        n = Negocio.objects.create(nombre='Auto Key Test')
        self.assertIsNotNone(n.api_key)
        self.assertEqual(len(n.api_key), 32)  # UUID hex = 32 chars
