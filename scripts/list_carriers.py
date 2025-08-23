import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from api import config

def list_argentina_carriers():
    """
    Fetches and prints the list of available carriers for Argentina from the Envia.com API.
    """
    # Use the configured environment to determine the correct base URL
    if config.ENVIRONMENT == "TEST":
        api_base_url = config.ENVIA_API_URL.replace("ship-test", "queries-test")
    else:
        api_base_url = config.ENVIA_API_URL.replace("api", "queries")

    api_url = f"{api_base_url}/carrier?country_code=AR"
    
    if not config.TOKEN:
        print("Error: TOKEN no estÃ¡ definido en el archivo .env")
        return

    headers = config.API_HEADERS

    print(f"--- Obteniendo listado de transportistas para Argentina ---")
    print(f"Entorno: {config.ENVIRONMENT}")
    print(f"URL: {api_url}")

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        
        carriers = response.json().get('data', [])
        
        print("\n--- Ã‰XITO ---")
        if carriers:
            print("Transportistas disponibles en Argentina (AR):")
            for carrier in carriers:
                print(f"- {carrier.get('name')} (carrier_code: {carrier.get('carrier_code')})")
        else:
            print("No se encontraron transportistas disponibles para Argentina.")

    except requests.exceptions.HTTPError as e:
        print("\n--- HTTP ERROR ---")
        print(f"Status Code: {e.response.status_code}")
        print("Respuesta:")
        print(e.response.text)
    except requests.exceptions.RequestException as e:
        print(f"\n--- ERROR DE CONEXIÃ“N ---")
        print(f"OcurriÃ³ un error: {e}")

if __name__ == "__main__":
    list_argentina_carriers()
