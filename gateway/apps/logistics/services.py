import requests
from django.conf import settings
from .exceptions import EnviaAPIError


def get_carriers_from_envia() -> list:
    """
    Obtiene la lista de carriers desde la API de Envia.com
    """
    # Configurar URL según entorno
    if settings.ENVIA_ENVIRONMENT == 'TEST':
        api_base_url = settings.ENVIA_API_URL.replace('ship-test', 'queries-test')
    else:
        api_base_url = settings.ENVIA_API_URL.replace('api', 'queries')

    api_url = f"{api_base_url}/carrier?country_code=AR"

    if not settings.ENVIA_TOKEN:
        raise EnviaAPIError(500, "Token de la API de Envia.com no está configurado")

    try:
        response = requests.get(api_url, headers=settings.ENVIA_API_HEADERS, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            result = response.json()
            carriers_data = result.get('data', [])

            carriers = []
            for carrier_data in carriers_data:
                name = carrier_data.get('name', '').lower()

                # Determinar categoría
                category = 'otros'
                if name in ['dhl', 'fedex', 'ups']:
                    category = 'internacional'
                elif 'correo' in name:
                    category = 'postal'
                elif name in ['oca', 'andreani', 'urbano', 'rueddo']:
                    category = 'local'
                elif name in ['dpd']:
                    category = 'europeo'

                carrier = {
                    'id': carrier_data.get('id'),
                    'name': carrier_data.get('name'),
                    'carrier_code': carrier_data.get('carrier_code'),
                    'description': carrier_data.get('description'),
                    'active': carrier_data.get('active'),
                    'country': carrier_data.get('country', 'AR'),
                    'category': category,
                }
                carriers.append(carrier)

            return carriers
        else:
            raise EnviaAPIError(
                response.status_code,
                f"Error al obtener carriers de Envia.com: {response.text}"
            )

    except requests.exceptions.RequestException as e:
        raise EnviaAPIError(503, f"No se pudo conectar con la API de Envia.com: {str(e)}")


def get_carrier_by_name(carrier_name: str) -> dict | None:
    """
    Obtiene información de un carrier específico por nombre
    """
    carriers = get_carriers_from_envia()

    for carrier in carriers:
        if carrier['name'].lower() == carrier_name.lower():
            return carrier

    return None


def get_config_info() -> dict:
    """
    Obtiene información de la configuración actual
    """
    return {
        'environment': settings.ENVIA_ENVIRONMENT,
        'api_url': settings.ENVIA_API_URL,
        'token_configured': bool(settings.ENVIA_TOKEN),
        'available_environments': ['TEST', 'PRO'],
    }
