import requests
from django.conf import settings
from .exceptions import EnviaAPIError


def get_rates(quote_data: dict) -> dict:
    api_url = f"{settings.ENVIA_API_URL}/ship/rate/"

    if not settings.ENVIA_TOKEN:
        raise EnviaAPIError(
            500,
            "El token de la API de Envia.com no está configurado. Por favor, defina la variable de entorno TOKEN."
        )

    origin = quote_data['origin']
    destination = quote_data['destination']

    origin_address = {
        'name': origin['contact_name'],
        'email': origin['contact_email'],
        'phone': origin['contact_phone'],
        'street': origin['street'],
        'number': origin['number'],
        'district': 'Default',
        'city': origin['city'],
        'state': origin['state'],
        'country': origin['country_code'],
        'postalCode': origin['postal_code'],
    }

    destination_address = {
        'name': destination['contact_name'],
        'email': destination['contact_email'],
        'phone': destination['contact_phone'],
        'street': destination['street'],
        'number': destination['number'],
        'district': 'Default',
        'city': destination['city'],
        'state': destination['state'],
        'country': destination['country_code'],
        'postalCode': destination['postal_code'],
    }

    packages = [
        {
            'content': p['content'],
            'weight': p['weight'],
            'dimensions': {
                'length': p['length'],
                'width': p['width'],
                'height': p['height'],
            },
        }
        for p in quote_data['parcels']
    ]

    carrier = quote_data.get('carrier') or 'fedex'

    payload = {
        'origin': origin_address,
        'destination': destination_address,
        'packages': packages,
        'shipment': {'carrier': carrier},
        'settings': {'currency': quote_data.get('currency', 'ARS')},
    }

    try:
        response = requests.post(api_url, headers=settings.ENVIA_API_HEADERS, json=payload)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as err:
        raise EnviaAPIError(
            err.response.status_code,
            f"Error al comunicarse con la API de Envia.com: {err.response.text}"
        )
    except requests.exceptions.RequestException as err:
        raise EnviaAPIError(
            503,
            f"No se pudo establecer conexión con la API de Envia.com: {err}"
        )
