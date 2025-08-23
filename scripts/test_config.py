import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import config
import requests
import json

def test_configuration():
    """
    Prueba la configuración actual y verifica conectividad con Envia.com
    """
    print("=== PRUEBA DE CONFIGURACIÓN ===")
    print(f"Entorno: {config.CONFIG_INFO['environment']}")
    print(f"URL API: {config.CONFIG_INFO['api_url']}")
    print(f"Token configurado: {config.CONFIG_INFO['token_configured']}")
    
    if not config.TOKEN:
        print("❌ ERROR: No hay token configurado")
        return False
        
    print(f"Token (primeros 10 chars): {config.TOKEN[:10]}...")
    print()
    
    return test_carriers_endpoint()

def test_carriers_endpoint():
    """
    Prueba el endpoint de carriers para Argentina
    """
    print("=== PROBANDO ENDPOINT DE CARRIERS ===")
    
    # Probamos con queries-test en lugar de ship-test para el endpoint de carriers
    if config.ENVIRONMENT == "TEST":
        api_base_url = config.ENVIA_API_URL.replace("ship-test", "queries-test")
    else:
        api_base_url = config.ENVIA_API_URL.replace("api", "queries")
    
    api_url = f"{api_base_url}/carrier?country_code=AR"
    
    headers = {
        "Authorization": f"Bearer {config.TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"URL: {api_url}")
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            carriers = response.json().get('data', [])
            print("EXITO - Carriers disponibles en Argentina:")
            for carrier in carriers[:5]:  # Mostrar solo los primeros 5
                print(f"  - {carrier.get('name', 'N/A')}")
            if len(carriers) > 5:
                print(f"  ... y {len(carriers) - 5} mas")
            return True
        else:
            print("ERROR - Respuesta:")
            print(response.text[:500])
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR DE CONEXION: {e}")
        return False

def test_shipping_quote():
    """
    Prueba una cotización de envío
    """
    print("\n=== PROBANDO COTIZACIÓN DE ENVÍO ===")
    
    payload = {
        "origin": {
            "name": "Test Sender",
            "email": "test@example.com",
            "phone": "1122334455",
            "street": "Avenida Corrientes",
            "number": "1000",
            "district": "Centro",
            "city": "Buenos Aires",
            "state": "C",
            "country": "AR",
            "postalCode": "1000"
        },
        "destination": {
            "name": "Test Receiver",
            "email": "receiver@example.com", 
            "phone": "1122334455",
            "street": "Avenida Santa Fe",
            "number": "2000",
            "district": "Centro",
            "city": "Buenos Aires", 
            "state": "C",
            "country": "AR",
            "postalCode": "1010"
        },
        "packages": [{
            "content": "Test Package",
            "amount": 1,
            "type": "box",
            "weight": 1,
            "insurance": 0,
            "declaredValue": 100,
            "weightUnit": "KG",
            "lengthUnit": "CM",
            "dimensions": {
                "length": 20,
                "width": 20,
                "height": 10
            }
        }],
        "shipment": {
            "carrier": "oca",
            "type": 0
        },
        "settings": {
            "currency": "ARS"
        }
    }
    
    api_url = f"{config.ENVIA_API_URL}/ship/rate/"
    
    try:
        response = requests.post(
            api_url, 
            headers=config.API_HEADERS, 
            json=payload,
            timeout=15
        )
        
        print(f"URL: {api_url}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("EXITO - Cotizacion obtenida:")
            print(json.dumps(result, indent=2)[:500] + "..." if len(str(result)) > 500 else json.dumps(result, indent=2))
            return True
        else:
            print("ERROR - Respuesta:")
            print(response.text[:500])
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR DE CONEXION: {e}")
        return False

if __name__ == "__main__":
    print("INICIANDO PRUEBAS DE CONFIGURACIÓN DE ENVIA.COM")
    print("=" * 50)
    
    config_ok = test_configuration()
    
    if config_ok:
        test_shipping_quote()
    else:
        print("\nNo se pueden realizar más pruebas debido a problemas de configuración.")
    
    print("\n" + "=" * 50)
    print("PRUEBAS COMPLETADAS")