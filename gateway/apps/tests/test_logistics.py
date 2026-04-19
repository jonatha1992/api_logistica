from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework.test import APIClient


VALID_QUOTE_PAYLOAD = {
    "origin": {
        "street": "Avenida Corrientes", "number": "1000",
        "city": "Buenos Aires", "state": "C", "postal_code": "1000",
        "country_code": "AR", "contact_name": "Sender",
        "contact_email": "sender@example.com", "contact_phone": "1122334455"
    },
    "destination": {
        "street": "Avenida Santa Fe", "number": "2000",
        "city": "Buenos Aires", "state": "C", "postal_code": "1010",
        "country_code": "AR", "contact_name": "Receiver",
        "contact_email": "receiver@example.com", "contact_phone": "1122334455"
    },
    "parcels": [{"weight": 1, "height": 10, "width": 20, "length": 20, "content": "Test"}],
    "carrier": "oca",
    "currency": "ARS"
}


class StatusEndpointTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_status_ok(self):
        r = self.client.get('/api/v1/status')
        self.assertEqual(r.status_code, 200)
        self.assertIn('status', r.data)
        self.assertEqual(r.data['status'], 'operativo')
        self.assertIn('environment', r.data)
        self.assertIn('timestamp', r.data)

    def test_root_ok(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('version', r.data)


class CotizarEndpointTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('apps.logistics.client_envia.requests.post')
    @patch('apps.logistics.client_envia.settings')
    def test_cotizar_success(self, mock_settings, mock_post):
        mock_settings.ENVIA_TOKEN = 'fake-test-token'
        mock_settings.ENVIA_API_URL = 'https://ship-test.envia.com'
        mock_settings.ENVIA_API_HEADERS = {'Authorization': 'Bearer fake-test-token', 'Content-Type': 'application/json'}

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'data': [{'carrier': 'oca', 'price': 500}]}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        r = self.client.post('/api/v1/cotizar', VALID_QUOTE_PAYLOAD, format='json')
        self.assertEqual(r.status_code, 200)

    def test_cotizar_invalid_payload(self):
        r = self.client.post('/api/v1/cotizar', {'invalid': 'data'}, format='json')
        self.assertEqual(r.status_code, 400)

    @patch('apps.logistics.client_envia.requests.post')
    def test_cotizar_envia_error(self, mock_post):
        import requests as req
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = 'Internal Server Error'
        http_err = req.exceptions.HTTPError(response=mock_resp)
        mock_post.side_effect = lambda *a, **kw: (_ for _ in ()).throw(
            req.exceptions.HTTPError(response=mock_resp)
        )

        r = self.client.post('/api/v1/cotizar', VALID_QUOTE_PAYLOAD, format='json')
        self.assertIn(r.status_code, [500, 503, 502])


class CarriersEndpointTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('apps.logistics.services.requests.get')
    @patch('apps.logistics.services.settings')
    def test_carriers_success(self, mock_settings, mock_get):
        mock_settings.ENVIA_TOKEN = 'fake-test-token'
        mock_settings.ENVIA_ENVIRONMENT = 'TEST'
        mock_settings.ENVIA_API_URL = 'https://ship-test.envia.com'
        mock_settings.ENVIA_API_HEADERS = {'Authorization': 'Bearer fake-test-token', 'Content-Type': 'application/json'}

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'data': [
            {'id': 62, 'name': 'oca', 'active': True},
            {'id': 114, 'name': 'andreani', 'active': True},
        ]}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        r = self.client.get('/api/v1/carriers')
        self.assertEqual(r.status_code, 200)
        self.assertIn('total', r.data)
        self.assertIn('data', r.data)

    @patch('apps.logistics.services.requests.get')
    @patch('apps.logistics.services.settings')
    def test_carrier_detail_found(self, mock_settings, mock_get):
        mock_settings.ENVIA_TOKEN = 'fake-test-token'
        mock_settings.ENVIA_ENVIRONMENT = 'TEST'
        mock_settings.ENVIA_API_URL = 'https://ship-test.envia.com'
        mock_settings.ENVIA_API_HEADERS = {'Authorization': 'Bearer fake-test-token', 'Content-Type': 'application/json'}

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'data': [
            {'id': 62, 'name': 'oca', 'active': True},
        ]}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        r = self.client.get('/api/v1/carriers/oca')
        self.assertEqual(r.status_code, 200)

    @patch('apps.logistics.services.requests.get')
    @patch('apps.logistics.services.settings')
    def test_carrier_detail_not_found(self, mock_settings, mock_get):
        mock_settings.ENVIA_TOKEN = 'fake-test-token'
        mock_settings.ENVIA_ENVIRONMENT = 'TEST'
        mock_settings.ENVIA_API_URL = 'https://ship-test.envia.com'
        mock_settings.ENVIA_API_HEADERS = {'Authorization': 'Bearer fake-test-token', 'Content-Type': 'application/json'}

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'data': []}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        r = self.client.get('/api/v1/carriers/carrier_inexistente')
        self.assertEqual(r.status_code, 404)
