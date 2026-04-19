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

    def test_resend_api_key_encrypted_in_db(self):
        negocio = Negocio.objects.create(
            nombre='Test Resend Encriptación',
            resend_api_key='re_test_super_secreto',
        )
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT resend_api_key FROM tenants_negocio WHERE id = %s",
                [negocio.id]
            )
            raw = cursor.fetchone()[0]
        self.assertNotEqual(raw, 're_test_super_secreto')
        negocio.refresh_from_db()
        self.assertEqual(negocio.resend_api_key, 're_test_super_secreto')


class NegocioMeViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.negocio = Negocio.objects.create(
            nombre='Tienda Test',
            nombre_comercial='Mi Tienda',
            color_primario='#4f46e5',
            smtp_host='smtp.test.com',
            smtp_user='user@test.com',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.negocio.api_key}')

    def test_get_me_devuelve_negocio_propio(self):
        r = self.client.get('/api/v1/negocio/me')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['nombre'], 'Tienda Test')
        self.assertEqual(r.data['nombre_comercial'], 'Mi Tienda')
        self.assertEqual(r.data['color_primario'], '#4f46e5')
        self.assertEqual(r.data['api_key'], self.negocio.api_key)

    def test_get_me_incluye_estados_de_servicios(self):
        r = self.client.get('/api/v1/negocio/me')
        self.assertEqual(r.status_code, 200)
        self.assertIn('smtp_configurado', r.data)
        self.assertIn('resend_configurado', r.data)
        self.assertIn('mp_configurado', r.data)
        self.assertTrue(r.data['smtp_configurado'])
        self.assertFalse(r.data['resend_configurado'])
        self.assertFalse(r.data['mp_configurado'])

    def test_patch_me_actualiza_marca(self):
        r = self.client.patch('/api/v1/negocio/me', {
            'nombre_comercial': 'Nombre Nuevo',
            'color_primario': '#FF6B35',
            'icono_emoji': '🛒',
            'slogan': 'El mejor servicio',
        }, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['nombre_comercial'], 'Nombre Nuevo')
        self.assertEqual(r.data['color_primario'], '#FF6B35')
        self.negocio.refresh_from_db()
        self.assertEqual(self.negocio.nombre_comercial, 'Nombre Nuevo')

    def test_patch_me_no_afecta_otro_negocio(self):
        otro = Negocio.objects.create(nombre='Otro Negocio', nombre_comercial='Original')
        self.client.patch('/api/v1/negocio/me', {'nombre_comercial': 'Hackeado'}, format='json')
        otro.refresh_from_db()
        self.assertEqual(otro.nombre_comercial, 'Original')

    def test_get_me_sin_auth_devuelve_401(self):
        self.client.credentials()
        r = self.client.get('/api/v1/negocio/me')
        self.assertEqual(r.status_code, 401)
