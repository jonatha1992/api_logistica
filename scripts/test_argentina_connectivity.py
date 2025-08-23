import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import client_envia, schemas

def main():
    """
    Runs a connectivity test with the Envia.com API using Argentinian data.
    """
    print("--- Iniciando prueba de conectividad para Argentina ---")

    # 1. Definir los datos de la cotizaciÃ³n
    quote_data = schemas.QuoteRequest(
        origin=schemas.SimpleAddress(
            street="Avenida Patricias Argentinas",
            number="480",
            city="Ciudad Autonoma De Buenos Aires",
            state="C",
            postal_code="1405",
            country_code="AR",
            contact_name="Remitente de Prueba",
            contact_email="remitente@example.com",
            contact_phone="1122334455"
        ),
        destination=schemas.SimpleAddress(
            street="BartolomÃ© Mitre",
            number="816",
            city="Guernica",
            state="B",
            postal_code="1858",
            country_code="AR",
            contact_name="Destinatario de Prueba",
            contact_email="destinatario@example.com",
            contact_phone="1122334455"
        ),
        parcels=[
            schemas.SimpleParcel(
                weight=2,
                height=15,
                width=25,
                length=30,
                content="Libros y Documentos"
            )
        ],
        currency="ARS"
    )

    print("\nDatos de la solicitud:")
    print(quote_data.model_dump_json(indent=2))

    # 2. Llamar a la funciÃ³n get_rates
    try:
        print("\nEnviando solicitud a Envia.com...")
        rates_response = client_envia.get_rates(quote_data)
        
        print("\n--- Ã‰XITO ---")
        print("Respuesta de la API de Envia.com:")
        import json
        print(json.dumps(rates_response, indent=2))

    except Exception as e:
        print("\n--- ERROR ---")
        print(f"OcurriÃ³ un error durante la prueba: {e}")


if __name__ == "__main__":
    main()
