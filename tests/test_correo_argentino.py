#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from api import config
import requests

def test_correo_argentino():
    """
    Prueba específica con Correo Argentino para ver si está disponible
    """
    
    print("=== PRUEBA CORREO ARGENTINO ===")
    print(f"Entorno: {config.ENVIRONMENT}")
    print()
    
    # Mismas direcciones de la prueba anterior
    payload = {
        "origin": {
            "street": "Pareja",
            "number": "6542", 
            "city": "Gonzalez Catan",
            "state": "B",  # Buenos Aires
            "postal_code": "1757",
            "country_code": "AR",
            "contact_name": "Remitente Test",
            "contact_email": "remitente@test.com",
            "contact_phone": "1122334455"
        },
        "destination": {
            "street": "Del Leon", 
            "number": "504",
            "city": "Ezeiza",
            "state": "B",  # Buenos Aires
            "postal_code": "1802",
            "country_code": "AR", 
            "contact_name": "Destinatario Test",
            "contact_email": "destinatario@test.com",
            "contact_phone": "1122334455"
        },
        "parcels": [
            {
                "weight": 1,
                "height": 10,
                "width": 20, 
                "length": 20,
                "content": "Paquete de prueba"
            }
        ],
        "carrier": "correoargentino",  # Probar diferentes variaciones
        "currency": "ARS"
    }
    
    print("1. PROBANDO CON 'correoargentino'")
    test_carrier_variation(payload.copy(), "correoargentino")
    
    print("\n" + "="*50 + "\n")
    
    print("2. PROBANDO CON 'correo-argentino'")
    payload["carrier"] = "correo-argentino"
    test_carrier_variation(payload.copy(), "correo-argentino")
    
    print("\n" + "="*50 + "\n")
    
    print("3. PROBANDO CON 'correo_argentino'")
    payload["carrier"] = "correo_argentino"
    test_carrier_variation(payload.copy(), "correo_argentino")
    
    print("\n" + "="*50 + "\n")
    
    print("4. PROBANDO SIN ESPECIFICAR CARRIER (ver si aparece en resultados)")
    payload_sin_carrier = payload.copy()
    del payload_sin_carrier["carrier"]  # Quitar carrier para que devuelva todos
    test_all_carriers(payload_sin_carrier)

def test_carrier_variation(payload, carrier_name):
    """
    Prueba una variación del nombre de Correo Argentino
    """
    try:
        api_url = "http://localhost:8000/api/v1/cotizar"
        
        print(f"Probando carrier: '{carrier_name}'")
        print(f"URL: {api_url}")
        
        response = requests.post(api_url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("RESPUESTA EXITOSA")
            
            if 'data' in result and result['data']:
                print(f"Cotizaciones encontradas: {len(result['data'])}")
                
                for i, quote in enumerate(result['data'], 1):
                    carrier = quote.get('carrier', 'N/A')
                    carrier_desc = quote.get('carrierDescription', 'N/A')
                    service_desc = quote.get('serviceDescription', 'N/A')
                    price = quote.get('totalPrice', 'N/A')
                    
                    print(f"  {i}. {carrier_desc} ({carrier}) - {service_desc} - ${price} ARS")
            else:
                print("No se encontraron cotizaciones")
                
        else:
            print(f"ERROR: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Detalle: {error_detail}")
            except:
                print(f"Respuesta: {response.text[:200]}...")
                
    except Exception as e:
        print(f"ERROR: {str(e)}")

def test_all_carriers(payload):
    """
    Prueba sin especificar carrier para ver todos los disponibles
    """
    try:
        api_url = "http://localhost:8000/api/v1/cotizar"
        
        print("Obteniendo cotizaciones de TODOS los carriers disponibles...")
        print(f"URL: {api_url}")
        
        response = requests.post(api_url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("RESPUESTA EXITOSA")
            
            if 'data' in result and result['data']:
                print(f"Total de cotizaciones: {len(result['data'])}")
                
                # Agrupar por carrier
                carriers_found = {}
                for quote in result['data']:
                    carrier = quote.get('carrier', 'unknown')
                    carrier_desc = quote.get('carrierDescription', 'N/A')
                    
                    if carrier not in carriers_found:
                        carriers_found[carrier] = {
                            'description': carrier_desc,
                            'services': []
                        }
                    
                    carriers_found[carrier]['services'].append({
                        'service': quote.get('serviceDescription', 'N/A'),
                        'price': quote.get('totalPrice', 'N/A')
                    })
                
                print(f"\nCARRIERS DISPONIBLES PARA ESTA RUTA:")
                print("-" * 50)
                
                for carrier, info in carriers_found.items():
                    print(f"\n{info['description']} ({carrier}):")
                    for service in info['services']:
                        print(f"  - {service['service']}: ${service['price']} ARS")
                        
                # Verificar específicamente si hay algún carrier con "correo" en el nombre
                correo_carriers = [c for c in carriers_found.keys() if 'correo' in c.lower()]
                if correo_carriers:
                    print(f"\nCARRIERS CON 'CORREO' ENCONTRADOS:")
                    for carrier in correo_carriers:
                        print(f"  - {carrier}")
                else:
                    print(f"\nNO SE ENCONTRARON CARRIERS CON 'CORREO' EN EL NOMBRE")
                    
            else:
                print("No se encontraron cotizaciones")
                
        else:
            print(f"ERROR: {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")

def check_available_carriers():
    """
    Verifica qué carriers están disponibles en Argentina según la API
    """
    try:
        print("\n" + "="*60)
        print("VERIFICANDO CARRIERS DISPONIBLES EN ARGENTINA")
        print("="*60)
        
        api_url = "http://localhost:8000/api/v1/carriers"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result:
                carriers = result['data']
                print(f"Total carriers disponibles: {len(carriers)}")
                
                correo_carriers = []
                other_carriers = []
                
                for carrier in carriers:
                    name = carrier.get('name', 'N/A')
                    description = carrier.get('description', 'N/A') 
                    category = carrier.get('category', 'N/A')
                    
                    if 'correo' in name.lower():
                        correo_carriers.append(carrier)
                    else:
                        other_carriers.append(carrier)
                
                if correo_carriers:
                    print(f"\nCARRIERS CON 'CORREO':")
                    for carrier in correo_carriers:
                        print(f"  - {carrier.get('name')} (ID: {carrier.get('id')}) - {carrier.get('description', 'N/A')}")
                else:
                    print(f"\nNO HAY CARRIERS CON 'CORREO' EN LA LISTA")
                
                print(f"\nTODOS LOS CARRIERS DISPONIBLES:")
                for carrier in carriers:
                    print(f"  - {carrier.get('name')} (ID: {carrier.get('id')}) - Categoria: {carrier.get('category')}")
                    
        else:
            print(f"Error al obtener lista de carriers: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    print("INVESTIGACION: CORREO ARGENTINO EN ENVIA.COM")
    print("="*60)
    
    # Primero verificar qué carriers están disponibles
    check_available_carriers()
    
    # Luego probar cotizaciones
    test_correo_argentino()
    
    print(f"\nINVESTIGACION COMPLETADA")

if __name__ == "__main__":
    main()