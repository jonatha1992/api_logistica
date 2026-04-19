#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from api import config
import requests

def test_argentina_quotation():
    """
    Prueba de cotizacion con direcciones reales de Argentina
    Desde: Gonzalez Catan, La Matanza, Buenos Aires
    Hasta: Ezeiza, Buenos Aires
    """
    
    print("=== PRUEBA DE COTIZACION ARGENTINA ===")
    print(f"Entorno: {config.ENVIRONMENT}")
    print(f"API URL: {config.ENVIA_API_URL}")
    print()
    
    # Datos de la cotización - González Catán a Ezeiza
    payload = {
        "origin": {
            "street": "Pareja",
            "number": "6542", 
            "city": "Gonzalez Catan",
            "state": "B",  # Buenos Aires
            "postal_code": "1757",  # CP de Gonzalez Catan
            "country_code": "AR",
            "contact_name": "Remitente Test",
            "contact_email": "remitente@test.com",
            "contact_phone": "1122334455"
        },
        "destination": {
            "street": "Del León", 
            "number": "504",
            "city": "Ezeiza",
            "state": "B",  # Buenos Aires
            "postal_code": "1802",  # CP de Ezeiza
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
        "carrier": "oca",
        "currency": "ARS"
    }
    
    # Test con OCA
    print("1. PROBANDO CON OCA")
    print("-" * 40)
    test_carrier(payload.copy(), "oca")
    
    print("\n" + "="*50 + "\n")
    
    # Test con Andreani
    print("2. PROBANDO CON ANDREANI") 
    print("-" * 40)
    payload_andreani = payload.copy()
    payload_andreani["carrier"] = "andreani"
    test_carrier(payload_andreani, "andreani")

def test_carrier(payload, carrier_name):
    """
    Prueba cotización con un carrier específico
    """
    try:
        # Usar nuestra API local
        api_url = "http://localhost:8000/api/v1/cotizar"
        
        print(f"Carrier: {carrier_name.upper()}")
        print(f"Origen: {payload['origin']['street']} {payload['origin']['number']}, {payload['origin']['city']}")
        print(f"Destino: {payload['destination']['street']} {payload['destination']['number']}, {payload['destination']['city']}")
        print(f"URL: {api_url}")
        print()
        
        response = requests.post(api_url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("COTIZACION EXITOSA")
            
            # Mostrar información de la respuesta
            if 'data' in result and result['data']:
                print(f"Cotizaciones disponibles: {len(result['data'])}")
                
                for i, quote in enumerate(result['data'][:3], 1):  # Mostrar máximo 3 cotizaciones
                    print(f"\n=== COTIZACION {i} ===")
                    print(f"Carrier: {quote.get('carrierDescription', quote.get('carrier', 'N/A'))}")
                    print(f"Servicio: {quote.get('serviceDescription', 'N/A')}")
                    print(f"Codigo Servicio: {quote.get('service', 'N/A')}")
                    print(f"Precio Total: ${quote.get('totalPrice', 'N/A')} {quote.get('currency', 'ARS')}")
                    print(f"Precio Base: ${quote.get('basePrice', 'N/A')} + Impuestos: ${quote.get('basePriceTaxes', 'N/A')}")
                    print(f"Tiempo de Entrega: {quote.get('deliveryEstimate', 'N/A')}")
                    
                    if quote.get('deliveryDate'):
                        delivery_info = quote['deliveryDate']
                        print(f"Fecha de Entrega: {delivery_info.get('date', 'N/A')} ({delivery_info.get('dateDifference', 'N/A')} dias)")
                    
                    # Información de modalidad de entrega
                    drop_off = quote.get('dropOff', 0)
                    if drop_off == 0:
                        print("Modalidad: Puerta a Puerta")
                    elif drop_off == 1:
                        print("Modalidad: Sucursal a Puerta")
                    elif drop_off == 2:
                        print("Modalidad: Puerta a Sucursal")
                    else:
                        print(f"Modalidad: Drop-off {drop_off}")
                    
                    # Si hay sucursales disponibles
                    if quote.get('branches') and len(quote['branches']) > 0:
                        branch = quote['branches'][0]  # Mostrar la primera sucursal
                        print(f"Sucursal: {branch.get('reference', 'N/A')}")
                        if branch.get('address'):
                            addr = branch['address']
                            print(f"Direccion: {addr.get('street', '')} {addr.get('number', '')}, {addr.get('city', '')}")
                    
                    print("-" * 40)
            else:
                print("No se encontraron cotizaciones en la respuesta")
                print(f"Respuesta completa: {json.dumps(result, indent=2)[:500]}...")
                
        else:
            print(f"ERROR: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Detalle del error: {error_detail}")
            except:
                print(f"Respuesta: {response.text[:200]}...")
                
    except requests.exceptions.ConnectionError:
        print("ERROR DE CONEXION")
        print("La API local no está ejecutándose. Ejecuta:")
        print("uvicorn api.main:app --reload --port 8000")
        
    except requests.exceptions.Timeout:
        print("TIMEOUT - La solicitud tardo demasiado")
        
    except Exception as e:
        print(f"ERROR INESPERADO: {str(e)}")

def main():
    print("PRUEBA DE COTIZACIONES ARGENTINA")
    print("Gonzalez Catan -> Ezeiza")
    print("="*50)
    
    test_argentina_quotation()
    
    print(f"\nPRUEBA COMPLETADA")

if __name__ == "__main__":
    main()