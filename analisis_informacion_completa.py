#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from api import config
import requests

def analizar_informacion_completa():
    """
    Analiza toda la información que puede proporcionar la API más allá de cotizaciones básicas
    """
    
    print("=== ANALISIS DE INFORMACION COMPLETA ===")
    print("Microservicio: OCA + Andreani + Correo Argentino")
    print("="*60)
    
    # Direcciones de prueba
    payload = {
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
        "currency": "ARS"
    }
    
    carriers = ["oca", "andreani", "correoargentino"]
    
    for carrier in carriers:
        print(f"\n{'='*20} {carrier.upper()} {'='*20}")
        analizar_carrier_detallado(payload.copy(), carrier)

def analizar_carrier_detallado(payload, carrier_name):
    """
    Análisis detallado de un carrier específico
    """
    payload["carrier"] = carrier_name
    
    try:
        api_url = "http://localhost:8000/api/v1/cotizar"
        response = requests.post(api_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'data' in result and result['data']:
                print(f"Servicios disponibles: {len(result['data'])}")
                
                for i, quote in enumerate(result['data'], 1):
                    print(f"\n--- SERVICIO {i}: {quote.get('serviceDescription', 'N/A')} ---")
                    
                    # INFORMACIÓN BÁSICA
                    print("INFORMACIÓN BÁSICA:")
                    print(f"  Carrier: {quote.get('carrierDescription', 'N/A')} (ID: {quote.get('carrierId', 'N/A')})")
                    print(f"  Servicio: {quote.get('serviceDescription', 'N/A')}")
                    print(f"  Código de servicio: {quote.get('service', 'N/A')} (ID: {quote.get('serviceId', 'N/A')})")
                    
                    # PRECIOS DETALLADOS
                    print("\nPRECIOS DETALLADOS:")
                    print(f"  Precio base: ${quote.get('basePrice', 0):,.2f} ARS")
                    print(f"  Impuestos: ${quote.get('basePriceTaxes', 0):,.2f} ARS")
                    print(f"  Tarifa extendida: ${quote.get('extendedFare', 0):,.2f} ARS")
                    print(f"  Seguro: ${quote.get('insurance', 0):,.2f} ARS")
                    print(f"  Servicios adicionales: ${quote.get('additionalServices', 0):,.2f} ARS")
                    print(f"  Cargos adicionales: ${quote.get('additionalCharges', 0):,.2f} ARS")
                    print(f"  PRECIO TOTAL: ${quote.get('totalPrice', 0):,.2f} ARS")
                    
                    # TIEMPOS DE ENTREGA
                    print("\nTIEMPOS DE ENTREGA:")
                    print(f"  Estimación: {quote.get('deliveryEstimate', 'N/A')}")
                    if quote.get('deliveryDate'):
                        delivery = quote['deliveryDate']
                        print(f"  Fecha específica: {delivery.get('date', 'N/A')} a las {delivery.get('time', 'N/A')}")
                        print(f"  Días de diferencia: {delivery.get('dateDifference', 'N/A')} {delivery.get('timeUnit', 'días')}")
                    
                    # MODALIDAD DE ENTREGA
                    print("\nMODALIDAD DE ENTREGA:")
                    drop_off = quote.get('dropOff', 0)
                    modalidades = {
                        0: "Puerta a Puerta",
                        1: "Sucursal a Puerta", 
                        2: "Puerta a Sucursal",
                        3: "Sucursal a Sucursal"
                    }
                    print(f"  Modalidad: {modalidades.get(drop_off, f'Drop-off {drop_off}')}")
                    print(f"  Zona: {quote.get('zone', 'N/A')}")
                    
                    # SUCURSALES DISPONIBLES
                    if quote.get('branches') and len(quote['branches']) > 0:
                        print(f"\nSUCURSALES DISPONIBLES ({len(quote['branches'])}):")
                        for j, branch in enumerate(quote['branches'][:2], 1):  # Mostrar max 2
                            print(f"  Sucursal {j}:")
                            print(f"    Nombre: {branch.get('reference', 'N/A')}")
                            print(f"    ID: {branch.get('branch_id', 'N/A')} (Código: {branch.get('branch_code', 'N/A')})")
                            if branch.get('address'):
                                addr = branch['address']
                                print(f"    Dirección: {addr.get('street', '')} {addr.get('number', '')}")
                                print(f"    Ciudad: {addr.get('city', 'N/A')}, CP: {addr.get('postalCode', 'N/A')}")
                                if addr.get('latitude') and addr.get('longitude'):
                                    print(f"    Coordenadas: {addr.get('latitude')}, {addr.get('longitude')}")
                            if branch.get('distance'):
                                print(f"    Distancia: {branch.get('distance')} km")
                    
                    # INFORMACIÓN DE PAQUETES
                    if quote.get('packageDetails'):
                        pkg = quote['packageDetails']
                        print(f"\nDETALLES DEL PAQUETE:")
                        print(f"  Peso total: {pkg.get('totalWeight', 'N/A')} {pkg.get('weightUnit', 'KG')}")
                        if pkg.get('details'):
                            for detail in pkg['details']:
                                print(f"  Peso aplicado: {detail.get('weight', 'N/A')} {detail.get('weightUnit', 'KG')} ({detail.get('appliedWeightType', 'N/A')})")
                    
                    # SERVICIOS ADICIONALES DISPONIBLES
                    print(f"\nSERVICIOS ADICIONALES:")
                    print(f"  Contra reembolso: {'Sí' if quote.get('cashOnDeliveryAmount', 0) > 0 else 'No'}")
                    print(f"  SMS: ${quote.get('smsCost', 0)} ARS")
                    print(f"  WhatsApp: ${quote.get('whatsappCost', 0)} ARS")
                    print(f"  Clave personalizada: {'Sí' if quote.get('customKey', False) else 'No'}")
                    print(f"  MercadoPago Shipping: {'Sí' if quote.get('isMps', False) else 'No'}")
                    
                    # INFORMACIÓN ADICIONAL
                    if quote.get('importFee', 0) > 0:
                        print(f"  Tarifa de importación: ${quote.get('importFee', 0)} ARS")
                    
                    print("-" * 60)
            else:
                print("No se encontraron servicios disponibles")
                
        else:
            print(f"Error: {response.status_code}")
            try:
                error = response.json()
                print(f"Detalle: {error}")
            except:
                print(f"Respuesta: {response.text[:200]}...")
                
    except Exception as e:
        print(f"Error: {str(e)}")

def obtener_informacion_carriers():
    """
    Obtiene información detallada de los carriers desde la API
    """
    print(f"\n{'='*60}")
    print("INFORMACIÓN DETALLADA DE CARRIERS")
    print("="*60)
    
    try:
        # Obtener información general de carriers
        api_url = "http://localhost:8000/api/v1/carriers"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            carriers = result.get('data', [])
            
            # Filtrar solo los 3 que nos interesan
            carriers_objetivo = ['oca', 'andreani', 'correoargentino']
            
            for carrier_name in carriers_objetivo:
                carrier_info = next((c for c in carriers if c.get('name', '').lower() == carrier_name), None)
                
                if carrier_info:
                    print(f"\n{carrier_name.upper()}:")
                    print(f"  ID: {carrier_info.get('id', 'N/A')}")
                    print(f"  Nombre: {carrier_info.get('name', 'N/A')}")
                    print(f"  Código: {carrier_info.get('carrier_code', 'N/A')}")
                    print(f"  Descripción: {carrier_info.get('description', 'N/A')}")
                    print(f"  Categoría: {carrier_info.get('category', 'N/A')}")
                    print(f"  País: {carrier_info.get('country', 'N/A')}")
                    print(f"  Activo: {'Sí' if carrier_info.get('active', False) else 'No'}")
                
                # Obtener información específica del carrier
                try:
                    detail_url = f"http://localhost:8000/api/v1/carriers/{carrier_name}"
                    detail_response = requests.get(detail_url, timeout=10)
                    
                    if detail_response.status_code == 200:
                        detail_info = detail_response.json()
                        print(f"  Información adicional disponible: Sí")
                    else:
                        print(f"  Información adicional: No disponible ({detail_response.status_code})")
                        
                except Exception:
                    print(f"  Información adicional: Error al obtener")
                    
        else:
            print(f"Error al obtener carriers: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def obtener_configuracion_api():
    """
    Obtiene información de configuración de la API
    """
    print(f"\n{'='*60}")
    print("CONFIGURACIÓN DE LA API")
    print("="*60)
    
    try:
        api_url = "http://localhost:8000/api/v1/config"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            config_info = response.json()
            
            print(f"Entorno actual: {config_info.get('environment', 'N/A')}")
            print(f"URL de la API: {config_info.get('api_url', 'N/A')}")
            print(f"Token configurado: {'Sí' if config_info.get('token_configured', False) else 'No'}")
            print(f"Entornos disponibles: {', '.join(config_info.get('available_environments', []))}")
            
        else:
            print(f"Error al obtener configuración: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    print("ANÁLISIS COMPLETO PARA MICROSERVICIO")
    print("Carriers objetivo: OCA, Andreani, Correo Argentino")
    print("="*80)
    
    # Información de configuración
    obtener_configuracion_api()
    
    # Información de carriers
    obtener_informacion_carriers()
    
    # Análisis detallado de cotizaciones
    analizar_informacion_completa()
    
    print(f"\n{'='*80}")
    print("ANÁLISIS COMPLETADO")
    print("="*80)

if __name__ == "__main__":
    main()