#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from api import config
import requests

def investigar_creacion_envios():
    """
    Investiga si la API permite crear envíos reales y obtener números de tracking
    """
    
    print("=== INVESTIGACION: CREACION DE ENVIOS Y TRACKING ===")
    print("Verificando endpoints disponibles para crear shipments")
    print("="*70)
    
    # Verificar endpoints disponibles en Envia.com
    endpoints_a_probar = [
        "/shipment",
        "/shipments", 
        "/ship",
        "/create",
        "/label",
        "/track"
    ]
    
    api_base = config.ENVIA_API_URL
    headers = config.API_HEADERS
    
    print(f"API Base: {api_base}")
    print(f"Headers configurados: {bool(headers.get('Authorization'))}")
    print()
    
    for endpoint in endpoints_a_probar:
        probar_endpoint(api_base + endpoint, headers, endpoint)

def probar_endpoint(url, headers, endpoint_name):
    """
    Prueba un endpoint específico para ver si existe
    """
    print(f"Probando: {endpoint_name}")
    print(f"URL: {url}")
    
    try:
        # Probar GET primero
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  GET {response.status_code}: ", end="")
        
        if response.status_code == 200:
            print("DISPONIBLE - Respuesta exitosa")
            try:
                data = response.json()
                print(f"    Estructura: {list(data.keys()) if isinstance(data, dict) else type(data).__name__}")
            except:
                print(f"    Contenido: {response.text[:100]}...")
                
        elif response.status_code == 401:
            print("REQUIERE AUTENTICACION")
            
        elif response.status_code == 404:
            print("No encontrado")
            
        elif response.status_code == 405:
            print("Método no permitido - Probar POST")
            # Si GET no funciona, probar POST
            try:
                post_response = requests.post(url, headers=headers, json={}, timeout=10)
                print(f"  POST {post_response.status_code}: ", end="")
                if post_response.status_code != 404:
                    print("ENDPOINT EXISTE para POST")
                else:
                    print("No encontrado")
            except:
                print("Error en POST")
                
        else:
            print(f"Status: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("TIMEOUT")
        
    except requests.exceptions.ConnectionError:
        print("ERROR DE CONEXION")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        
    print()

def investigar_documentacion_envia():
    """
    Busca información en la documentación de Envia.com sobre creación de envíos
    """
    print("="*70)
    print("BUSCANDO INFORMACION EN ENDPOINTS CONOCIDOS DE ENVIA.COM")
    print("="*70)
    
    # Endpoints conocidos según documentación típica de APIs de envíos
    endpoints_shipment = [
        ("POST", "/shipment", "Crear envío"),
        ("GET", "/shipment/{id}", "Obtener envío"),
        ("POST", "/label", "Generar etiqueta"),
        ("GET", "/track/{tracking}", "Rastrear envío"),
        ("GET", "/services", "Servicios disponibles"),
        ("POST", "/validate", "Validar dirección")
    ]
    
    api_base = config.ENVIA_API_URL
    headers = config.API_HEADERS
    
    for method, endpoint, description in endpoints_shipment:
        print(f"{method} {endpoint} - {description}")
        
        if method == "GET" and "{" not in endpoint:
            try:
                response = requests.get(api_base + endpoint, headers=headers, timeout=10)
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("  DISPONIBLE!")
                elif response.status_code == 401:
                    print("  Requiere autenticación")
                elif response.status_code == 404:
                    print("  No encontrado")
                else:
                    print(f"  Respuesta: {response.status_code}")
                    
            except Exception as e:
                print(f"  Error: {str(e)}")
                
        print()

def probar_crear_envio_prueba():
    """
    Intenta crear un envío de prueba para ver si es posible
    """
    print("="*70) 
    print("INTENTANDO CREAR ENVIO DE PRUEBA")
    print("="*70)
    
    # Datos básicos para crear un envío
    envio_data = {
        "origin": {
            "name": "Remitente Test",
            "company": "Test Company",
            "email": "test@example.com",
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
            "email": "dest@example.com",
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
            "service": "oca_PP",
            "type": 0
        },
        "settings": {
            "currency": "ARS"
        }
    }
    
    api_base = config.ENVIA_API_URL
    headers = config.API_HEADERS
    
    endpoints_crear = [
        "/shipment",
        "/shipments",
        "/ship"
    ]
    
    for endpoint in endpoints_crear:
        print(f"Probando crear envío en: {endpoint}")
        
        try:
            response = requests.post(
                api_base + endpoint,
                headers=headers,
                json=envio_data,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                print("SUCCESS - ENVIO CREADO!")
                result = response.json()
                print("INFORMACION DEL ENVIO:")
                print(json.dumps(result, indent=2)[:1000] + "...")
                
                # Buscar número de tracking
                tracking_fields = ['tracking', 'trackingNumber', 'tracking_number', 
                                 'guide', 'guia', 'shipmentId', 'id', 'folio']
                
                for field in tracking_fields:
                    if field in result:
                        print(f"TRACKING/GUIA ENCONTRADO: {field} = {result[field]}")
                
                return result
                
            elif response.status_code == 400:
                print("ERROR 400 - Datos inválidos")
                try:
                    error = response.json()
                    print(f"Detalle: {error}")
                except:
                    print(f"Respuesta: {response.text[:500]}")
                    
            elif response.status_code == 401:
                print("ERROR 401 - Sin autorización")
                
            elif response.status_code == 404:
                print("ERROR 404 - Endpoint no encontrado")
                
            else:
                print(f"ERROR {response.status_code}")
                print(f"Respuesta: {response.text[:300]}")
                
        except Exception as e:
            print(f"ERROR: {str(e)}")
            
        print("-" * 50)

def verificar_capacidades_api():
    """
    Verifica qué capacidades tiene la API actual
    """
    print("="*70)
    print("VERIFICANDO CAPACIDADES ACTUALES DE LA API")
    print("="*70)
    
    capacidades = {
        "Cotizaciones": "DISPONIBLE",
        "Lista de Carriers": "DISPONIBLE", 
        "Info de Carriers": "DISPONIBLE",
        "Configuracion": "DISPONIBLE",
        "Crear Envios": "POR VERIFICAR",
        "Numeros de Tracking": "POR VERIFICAR",
        "Etiquetas": "POR VERIFICAR",
        "Rastreo": "POR VERIFICAR"
    }
    
    for funcionalidad, status in capacidades.items():
        print(f"{funcionalidad:20} {status}")
    
    print()
    print("RECOMENDACIONES PARA MICROSERVICIO:")
    print("- Cotizaciones: LISTO para produccion")
    print("- Creacion de envios: Requiere investigacion adicional")
    print("- Tracking: Depende de si se pueden crear envios")

def main():
    print("INVESTIGACION: CAPACIDADES COMPLETAS DE LA API")
    print("="*80)
    
    # Verificar capacidades actuales
    verificar_capacidades_api()
    
    # Investigar endpoints de creación
    investigar_creacion_envios()
    
    # Buscar endpoints conocidos
    investigar_documentacion_envia()
    
    # Intentar crear un envío de prueba
    probar_crear_envio_prueba()
    
    print(f"\n{'='*80}")
    print("INVESTIGACION COMPLETADA")
    print("="*80)

if __name__ == "__main__":
    main()