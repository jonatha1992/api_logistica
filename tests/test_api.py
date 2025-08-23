# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
import requests

# Ajustamos la ruta para que Python encuentre el módulo de la aplicación
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.main import app
from api import client_envia

client = TestClient(app)

# --- Datos de prueba ---

VALID_QUOTE_PAYLOAD = {
    "origin": {
        "street": "Av. del Roble",
        "number": "660",
        "city": "San Pedro Garza Garcia",
        "state": "NL",
        "postal_code": "66265",
        "country_code": "MX",
        "contact_name": "John Doe",
        "contact_email": "john.doe@example.com",
        "contact_phone": "8181818181",
    },
    "destination": {
        "street": "Av. Constitucion",
        "number": "405",
        "city": "Monterrey",
        "state": "NL",
        "postal_code": "64000",
        "country_code": "MX",
        "contact_name": "Jane Doe",
        "contact_email": "jane.doe@example.com",
        "contact_phone": "8181818181",
    },
    "parcels": [
        {"weight": 1, "height": 10, "width": 20, "length": 20, "content": "Zapatos"}
    ],
    "carrier": "fedex",
    "currency": "MXN",
}

# --- Pruebas para Endpoints Básicos ---


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    response_data = response.json()
    assert "mensaje" in response_data
    assert "version" in response_data
    assert "environment" in response_data


def test_get_status():
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    response_data = response.json()
    assert "status" in response_data
    assert "environment" in response_data
    assert "timestamp" in response_data
    assert response_data["status"] == "operativo"


# --- Pruebas para el Endpoint de Cotización ---


def test_quote_success(monkeypatch):
    """Prueba el caso de éxito (200 OK) para una cotización, simulando la respuesta de Envia.com."""
    # 1. Preparamos la simulación (mock)
    mock_envia_response = {"data": [{"carrier": "fedex", "price": 150.00}]}

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_envia_response

    # 2. Sobrescribimos requests.post para que devuelva nuestra simulación
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: mock_response)

    # 3. Hacemos la llamada a nuestra API
    response = client.post("/api/v1/cotizar", json=VALID_QUOTE_PAYLOAD)

    # 4. Verificamos el resultado
    assert response.status_code == 200
    assert response.json() == mock_envia_response


def test_quote_envia_api_error(monkeypatch):
    """Prueba el manejo de un error 500 por parte de la API de Envia.com."""
    # 1. Preparamos la simulación de un error HTTP
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error from Envia"
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mock_response
    )

    # 2. Sobrescribimos requests.post
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: mock_response)

    # 3. Hacemos la llamada a nuestra API
    response = client.post("/api/v1/cotizar", json=VALID_QUOTE_PAYLOAD)

    # 4. Verificamos que nuestra API maneja el error y devuelve un 500
    assert response.status_code == 500
    assert "Error al comunicarse con la API de Envia.com" in response.json()["detail"]


def test_quote_invalid_payload():
    """Prueba que la API devuelva un error 422 si el payload es inválido."""
    invalid_payload = VALID_QUOTE_PAYLOAD.copy()
    del invalid_payload["origin"]  # Hacemos que el payload sea inválido

    response = client.post("/api/v1/cotizar", json=invalid_payload)

    assert response.status_code == 422
    # El detalle del error de validación es generado por FastAPI, solo verificamos que exista
    assert "detail" in response.json()


# --- Pruebas para Nuevos Endpoints ---

def test_get_config():
    """Prueba el endpoint de configuración."""
    response = client.get("/api/v1/config")
    assert response.status_code == 200
    response_data = response.json()
    
    # Verificar que contiene los campos esperados
    assert "environment" in response_data
    assert "api_url" in response_data
    assert "token_configured" in response_data
    assert "available_environments" in response_data
    
    # Verificar tipos de datos
    assert isinstance(response_data["token_configured"], bool)
    assert isinstance(response_data["available_environments"], list)
    assert response_data["environment"] in ["TEST", "PRO"]


def test_get_carriers_success(monkeypatch):
    """Prueba el endpoint de carriers con respuesta exitosa."""
    # Mock de la respuesta de Envia.com
    mock_carriers_response = {
        "data": [
            {"id": 62, "name": "oca"},
            {"id": 114, "name": "andreani"},
            {"id": 155, "name": "dhl"}
        ]
    }
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_carriers_response
    mock_response.raise_for_status.return_value = None
    
    # Sobrescribir requests.get
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: mock_response)
    
    # Hacer la llamada
    response = client.get("/api/v1/carriers")
    
    # Verificaciones
    assert response.status_code == 200
    response_data = response.json()
    
    assert "meta" in response_data
    assert "total" in response_data
    assert "data" in response_data
    assert response_data["meta"] == "carriers"
    assert response_data["total"] == 3
    assert len(response_data["data"]) == 3
    
    # Verificar estructura de carrier
    carrier = response_data["data"][0]
    assert "id" in carrier
    assert "name" in carrier
    assert "category" in carrier


def test_get_carrier_info_success(monkeypatch):
    """Prueba obtener información de un carrier específico."""
    # Mock de la respuesta de Envia.com
    mock_carriers_response = {
        "data": [
            {"id": 62, "name": "oca"},
            {"id": 114, "name": "andreani"}
        ]
    }
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_carriers_response
    mock_response.raise_for_status.return_value = None
    
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: mock_response)
    
    # Probar con carrier existente
    response = client.get("/api/v1/carriers/oca")
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert "id" in response_data
    assert "name" in response_data
    assert response_data["name"] == "oca"
    assert response_data["category"] == "local"


def test_get_carrier_info_not_found(monkeypatch):
    """Prueba obtener información de un carrier que no existe."""
    # Mock de respuesta vacía
    mock_carriers_response = {"data": []}
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_carriers_response
    mock_response.raise_for_status.return_value = None
    
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: mock_response)
    
    # Probar con carrier inexistente
    response = client.get("/api/v1/carriers/inexistente")
    
    assert response.status_code == 404
    response_data = response.json()
    assert "detail" in response_data
    assert "inexistente" in response_data["detail"]


def test_get_carriers_api_error(monkeypatch):
    """Prueba el manejo de errores al obtener carriers."""
    # Mock de error de conexión
    def mock_get_error(*args, **kwargs):
        raise requests.exceptions.ConnectionError("Connection failed")
    
    monkeypatch.setattr(requests, "get", mock_get_error)
    
    response = client.get("/api/v1/carriers")
    
    assert response.status_code == 503
    response_data = response.json()
    assert "detail" in response_data
    assert "conectar" in response_data["detail"].lower()
