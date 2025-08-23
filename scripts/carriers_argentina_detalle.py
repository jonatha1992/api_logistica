import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import config
import requests
import json

def get_argentina_carriers_detailed():
    """
    Obtiene información detallada de todos los carriers disponibles en Argentina
    """
    print("=== CARRIERS DISPONIBLES EN ARGENTINA ===")
    print(f"Entorno: {config.ENVIRONMENT}")
    print()
    
    # Configurar URL según entorno
    if config.ENVIRONMENT == "TEST":
        api_base_url = config.ENVIA_API_URL.replace("ship-test", "queries-test")
    else:
        api_base_url = config.ENVIA_API_URL.replace("api", "queries")
    
    api_url = f"{api_base_url}/carrier?country_code=AR"
    
    if not config.TOKEN:
        print("❌ ERROR: No hay token configurado")
        return
    
    headers = config.API_HEADERS
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            result = response.json()
            carriers = result.get('data', [])
            
            print(f"TOTAL DE CARRIERS: {len(carriers)}")
            print("=" * 60)
            
            for i, carrier in enumerate(carriers, 1):
                print(f"\n{i}. CARRIER: {carrier.get('name', 'N/A').upper()}")
                print(f"   ID: {carrier.get('id', 'N/A')}")
                print(f"   Código: {carrier.get('carrier_code', 'N/A')}")
                print(f"   Descripción: {carrier.get('description', 'N/A')}")
                print(f"   Activo: {carrier.get('active', 'N/A')}")
                print(f"   País: {carrier.get('country', 'N/A')}")
                
                # Información adicional si está disponible
                if carrier.get('services'):
                    print(f"   Servicios disponibles: {len(carrier.get('services', []))}")
                
                if carrier.get('website'):
                    print(f"   Sitio web: {carrier.get('website')}")
                
                print("-" * 40)
            
            # Resumen por tipo de carrier
            carrier_names = [c.get('name', 'N/A') for c in carriers]
            
            print(f"\nRESUMEN DE CARRIERS EN ARGENTINA:")
            print("=" * 50)
            
            # Categorizar carriers conocidos
            internacionales = [name for name in carrier_names if name.lower() in ['dhl', 'fedex', 'ups']]
            correos = [name for name in carrier_names if 'correo' in name.lower()]
            locales = [name for name in carrier_names if name.lower() in ['oca', 'andreani', 'urbano', 'rueddo']]
            otros = [name for name in carrier_names if name not in internacionales + correos + locales]
            
            if internacionales:
                print(f"Carriers Internacionales: {', '.join(internacionales)}")
            
            if correos:
                print(f"Servicios Postales: {', '.join(correos)}")
            
            if locales:
                print(f"Carriers Locales Argentinos: {', '.join(locales)}")
            
            if otros:
                print(f"Otros: {', '.join(otros)}")
                
            return carriers
        else:
            print(f"❌ ERROR: Status Code {response.status_code}")
            print(response.text[:500])
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")
        return None

def get_carrier_services(carrier_name):
    """
    Intenta obtener más información sobre los servicios de un carrier específico
    """
    print(f"\n=== SERVICIOS DE {carrier_name.upper()} ===")
    
    # Configurar URL según entorno  
    if config.ENVIRONMENT == "TEST":
        api_base_url = config.ENVIA_API_URL.replace("ship-test", "queries-test")
    else:
        api_base_url = config.ENVIA_API_URL.replace("api", "queries")
    
    # Intentar obtener servicios específicos del carrier
    api_url = f"{api_base_url}/carrier/{carrier_name}?country_code=AR"
    
    try:
        response = requests.get(api_url, headers=config.API_HEADERS, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Informacion detallada obtenida para {carrier_name}")
            print(json.dumps(result, indent=2)[:1000] + "..." if len(str(result)) > 1000 else json.dumps(result, indent=2))
        else:
            print(f"No hay informacion detallada disponible para {carrier_name} (Status: {response.status_code})")
            
    except requests.exceptions.RequestException as e:
        print(f"No se pudo obtener informacion detallada para {carrier_name}: {e}")

def main():
    print("INVESTIGACION DE CARRIERS DISPONIBLES EN ARGENTINA")
    print("=" * 60)
    
    # Obtener lista completa
    carriers = get_argentina_carriers_detailed()
    
    if carriers:
        print(f"\nANALISIS COMPLETADO")
        print(f"Se encontraron {len(carriers)} carriers disponibles en Argentina")
        
        # Intentar obtener información detallada de algunos carriers principales
        principales = ['oca', 'andreani', 'dhl', 'fedex']
        carriers_disponibles = [c.get('name', '').lower() for c in carriers]
        
        print(f"\nINTENTANDO OBTENER INFORMACION DETALLADA...")
        for carrier in principales:
            if carrier in carriers_disponibles:
                get_carrier_services(carrier)
    
    print(f"\nINVESTIGACION COMPLETADA")

if __name__ == "__main__":
    main()