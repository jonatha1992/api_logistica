#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from api import config
import requests

def probar_crear_shipment_directo():
    """
    Prueba crear un shipment directamente usando diferentes variaciones de la API de Envia.com
    """
    
    print("=== PRUEBA DIRECTA: CREAR SHIPMENT EN ENVIA.COM ===")
    print("="*60)
    
    # Datos del shipment basados en el formato que funciona para cotizaciones
    shipment_data = {
        "origin": {
            "name": "Remitente Test",
            "company": "Test Company",
            "email": "remitente@test.com",
            "phone": "1122334455",
            "street": "Pareja",
            "number": "6542",
            "district": "Gonzalez Catan",
            "city": "Gonzalez Catan",
            "state": "B",
            "country": "AR",
            "postalCode": "1757",
            "reference": "Casa azul"
        },
        "destination": {
            "name": "Destinatario Test",
            "company": "",
            "email": "destinatario@test.com",
            "phone": "1122334455",
            "street": "Del Leon",
            "number": "504",
            "district": "Ezeiza",
            "city": "Ezeiza",
            "state": "B",
            "country": "AR",
            "postalCode": "1802",
            "reference": "Depto 1"
        },
        "packages": [
            {
                "content": "Paquete de prueba",
                "amount": 1,
                "type": "box",
                "weight": 1,
                "insurance": 0,
                "declaredValue": 1000,
                "weightUnit": "KG",
                "lengthUnit": "CM",
                "dimensions": {
                    "length": 20,
                    "width": 20,
                    "height": 10
                }
            }
        ],
        "shipment": {
            "carrier": "oca",
            "service": "oca_PP",  # Servicio Puerta a Puerta que sabemos que funciona
            "type": 0
        },
        "settings": {
            "currency": "ARS",
            "printFormat": "PDF",
            "printSize": "STOCK_4X6"
        }
    }
    
    # URLs diferentes para probar
    base_urls = [
        config.ENVIA_API_URL,  # https://api.envia.com
        config.ENVIA_API_URL.replace("api", "ship"),  # https://ship.envia.com  
    ]
    
    # Endpoints para probar
    endpoints = [
        "shipment",
        "shipments", 
        "create",
        "generate",
        "ship"
    ]
    
    headers = config.API_HEADERS.copy()
    headers['Content-Type'] = 'application/json'
    
    for base_url in base_urls:
        print(f"\nProbando con base URL: {base_url}")
        print("-" * 50)
        
        for endpoint in endpoints:
            full_url = f"{base_url}/{endpoint}"
            print(f"\nEndpoint: POST {full_url}")
            
            try:
                response = requests.post(
                    full_url,
                    headers=headers,
                    json=shipment_data,
                    timeout=30
                )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    print("SUCCESS - SHIPMENT CREADO!")
                    try:
                        result = response.json()
                        print("RESPUESTA:")
                        print(json.dumps(result, indent=2)[:800] + "...")
                        
                        # Buscar campos de tracking
                        buscar_tracking_en_respuesta(result)
                        
                    except json.JSONDecodeError:
                        print("Respuesta no es JSON:")
                        print(response.text[:500])
                        
                elif response.status_code == 400:
                    print("ERROR 400 - Solicitud inválida")
                    try:
                        error = response.json()
                        print(f"Error detallado: {json.dumps(error, indent=2)}")
                    except:
                        print(f"Respuesta: {response.text[:300]}")
                        
                elif response.status_code == 401:
                    print("ERROR 401 - No autorizado")
                    
                elif response.status_code == 404:
                    print("ERROR 404 - Endpoint no existe")
                    
                elif response.status_code == 405:
                    print("ERROR 405 - Método no permitido")
                    
                elif response.status_code == 422:
                    print("ERROR 422 - Datos no válidos")
                    try:
                        error = response.json()
                        print(f"Errores de validación: {json.dumps(error, indent=2)}")
                    except:
                        print(f"Respuesta: {response.text[:300]}")
                        
                else:
                    print(f"Status: {response.status_code}")
                    print(f"Respuesta: {response.text[:200]}")
                    
            except requests.exceptions.Timeout:
                print("TIMEOUT - Solicitud tardó demasiado")
                
            except requests.exceptions.ConnectionError:
                print("ERROR DE CONEXION")
                
            except Exception as e:
                print(f"ERROR: {str(e)}")

def buscar_tracking_en_respuesta(data):
    """
    Busca números de tracking en la respuesta
    """
    tracking_fields = [
        'tracking', 'trackingNumber', 'tracking_number', 'trackingCode',
        'guide', 'guia', 'guiaNumber', 'numeroGuia',
        'shipmentId', 'id', 'folio', 'reference',
        'waybill', 'awb', 'label', 'labelId'
    ]
    
    print("\nBUSCANDO NUMEROS DE TRACKING:")
    
    def search_recursive(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # Verificar si es un campo de tracking
                if key.lower() in [f.lower() for f in tracking_fields]:
                    print(f"  TRACKING ENCONTRADO: {current_path} = {value}")
                
                # Buscar recursivamente
                search_recursive(value, current_path)
                
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                search_recursive(item, f"{path}[{i}]")
    
    search_recursive(data)

def probar_con_datos_cotizacion():
    """
    Usa los mismos datos que funcionaron en la cotización para intentar crear el envío
    """
    print("\n" + "="*60)
    print("PROBANDO CON DATOS DE COTIZACION EXITOSA")
    print("="*60)
    
    # Primero hacer una cotización para obtener los datos exactos
    print("1. Obteniendo cotización exitosa...")
    
    cotizacion_data = {
        "origin": {
            "street": "Pareja",
            "number": "6542", 
            "city": "Gonzalez Catan",
            "state": "B",
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
            "state": "B",
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
        "carrier": "oca",
        "currency": "ARS"
    }
    
    try:
        # Obtener cotización a través de nuestra API local
        response = requests.post(
            "http://localhost:8000/api/v1/cotizar",
            json=cotizacion_data,
            timeout=30
        )
        
        if response.status_code == 200:
            cotizacion_result = response.json()
            if 'data' in cotizacion_result and cotizacion_result['data']:
                primera_cotizacion = cotizacion_result['data'][0]
                
                print("Cotización exitosa obtenida:")
                print(f"  Carrier: {primera_cotizacion.get('carrierDescription')}")
                print(f"  Servicio: {primera_cotizacion.get('serviceDescription')}")
                print(f"  Código: {primera_cotizacion.get('service')}")
                print(f"  Precio: ${primera_cotizacion.get('totalPrice')} ARS")
                
                # Ahora intentar crear shipment con estos datos exactos
                print("\n2. Intentando crear shipment con estos datos...")
                
                # Convertir cotización a formato de shipment
                shipment_desde_cotizacion = convertir_cotizacion_a_shipment(
                    cotizacion_data, primera_cotizacion
                )
                
                # Intentar crear el shipment
                probar_crear_con_datos_exactos(shipment_desde_cotizacion)
                
        else:
            print(f"Error al obtener cotización: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def convertir_cotizacion_a_shipment(cotizacion_data, cotizacion_result):
    """
    Convierte datos de cotización exitosa a formato de shipment
    """
    return {
        "origin": {
            "name": cotizacion_data["origin"]["contact_name"],
            "company": "Test Company",
            "email": cotizacion_data["origin"]["contact_email"],
            "phone": cotizacion_data["origin"]["contact_phone"],
            "street": cotizacion_data["origin"]["street"],
            "number": cotizacion_data["origin"]["number"],
            "district": "",
            "city": cotizacion_data["origin"]["city"],
            "state": cotizacion_data["origin"]["state"],
            "country": cotizacion_data["origin"]["country_code"],
            "postalCode": cotizacion_data["origin"]["postal_code"],
            "reference": ""
        },
        "destination": {
            "name": cotizacion_data["destination"]["contact_name"],
            "company": "",
            "email": cotizacion_data["destination"]["contact_email"],
            "phone": cotizacion_data["destination"]["contact_phone"],
            "street": cotizacion_data["destination"]["street"],
            "number": cotizacion_data["destination"]["number"],
            "district": "",
            "city": cotizacion_data["destination"]["city"],
            "state": cotizacion_data["destination"]["state"],
            "country": cotizacion_data["destination"]["country_code"],
            "postalCode": cotizacion_data["destination"]["postal_code"],
            "reference": ""
        },
        "packages": [
            {
                "content": parcel["content"],
                "amount": 1,
                "type": "box",
                "weight": parcel["weight"],
                "insurance": 0,
                "declaredValue": 1000,
                "weightUnit": "KG",
                "lengthUnit": "CM",
                "dimensions": {
                    "length": parcel["length"],
                    "width": parcel["width"], 
                    "height": parcel["height"]
                }
            } for parcel in cotizacion_data["parcels"]
        ],
        "shipment": {
            "carrier": cotizacion_result.get("carrier"),
            "service": cotizacion_result.get("service"),
            "serviceId": cotizacion_result.get("serviceId"),
            "carrierId": cotizacion_result.get("carrierId"),
            "type": cotizacion_result.get("dropOff", 0)
        },
        "settings": {
            "currency": cotizacion_data["currency"],
            "printFormat": "PDF",
            "printSize": "STOCK_4X6"
        }
    }

def probar_crear_con_datos_exactos(shipment_data):
    """
    Intenta crear shipment con datos exactos de cotización exitosa
    """
    # Usar directamente la API de Envia.com
    url = f"{config.ENVIA_API_URL}/shipment"
    headers = config.API_HEADERS.copy()
    headers['Content-Type'] = 'application/json'
    
    print(f"Creando shipment en: {url}")
    print("Datos del shipment:")
    print(json.dumps(shipment_data, indent=2)[:600] + "...")
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=shipment_data,
            timeout=60  # Más tiempo para creación de shipment
        )
        
        print(f"\nRespuesta: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("SUCCESS! SHIPMENT CREADO")
            result = response.json()
            print("INFORMACION DEL SHIPMENT:")
            print(json.dumps(result, indent=2)[:1000] + "...")
            
            buscar_tracking_en_respuesta(result)
            return result
            
        else:
            print(f"Error {response.status_code}")
            try:
                error = response.json()
                print("Error detallado:")
                print(json.dumps(error, indent=2))
            except:
                print(f"Respuesta: {response.text[:500]}")
                
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    print("INVESTIGACION COMPLETA: CREAR SHIPMENTS Y TRACKING")
    print("="*70)
    
    # Probar diferentes endpoints
    probar_crear_shipment_directo()
    
    # Probar con datos exactos de cotización exitosa
    probar_con_datos_cotizacion()
    
    print("\n" + "="*70)
    print("INVESTIGACION DE SHIPMENTS COMPLETADA")
    print("="*70)

if __name__ == "__main__":
    main()