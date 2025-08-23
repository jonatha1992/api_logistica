# api_logistica/client_envia.py
import requests
from fastapi import HTTPException
from . import config
from .schemas import QuoteRequest, EnviaQuotePayload, EnviaAddress, EnviaParcel, EnviaDimensions, EnviaShipment, EnviaSettings

def get_rates(quote_data: QuoteRequest):
    api_url = f"{config.ENVIA_API_URL}/ship/rate/"

    if not config.TOKEN:
        raise HTTPException(
            status_code=500,
            detail="El token de la API de Envia.com no estÃ¡ configurado. Por favor, defina la variable de entorno TOKEN."
        )

    origin_address = EnviaAddress(
        name=quote_data.origin.contact_name,
        email=quote_data.origin.contact_email,
        phone=quote_data.origin.contact_phone,
        street=quote_data.origin.street,
        number=quote_data.origin.number,
        district="Default",
        city=quote_data.origin.city,
        state=quote_data.origin.state,
        country=quote_data.origin.country_code,
        postalCode=quote_data.origin.postal_code,
    )

    destination_address = EnviaAddress(
        name=quote_data.destination.contact_name,
        email=quote_data.destination.contact_email,
        phone=quote_data.destination.contact_phone,
        street=quote_data.destination.street,
        number=quote_data.destination.number,
        district="Default",
        city=quote_data.destination.city,
        state=quote_data.destination.state,
        country=quote_data.destination.country_code,
        postalCode=quote_data.destination.postal_code,
    )

    packages = [
        EnviaParcel(
            content=p.content,
            weight=p.weight,
            dimensions=EnviaDimensions(
                length=p.length,
                width=p.width,
                height=p.height
            )
        ) for p in quote_data.parcels
    ]

    carrier = quote_data.carrier or "fedex"

    payload = EnviaQuotePayload(
        origin=origin_address,
        destination=destination_address,
        packages=packages,
        shipment=EnviaShipment(carrier=carrier),
        settings=EnviaSettings(currency=quote_data.currency)
    )

    try:
        response = requests.post(api_url, headers=config.API_HEADERS, json=payload.model_dump())
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as err:
        raise HTTPException(
            status_code=err.response.status_code,
            detail=f"Error al comunicarse con la API de Envia.com: {err.response.text}"
        )
    except requests.exceptions.RequestException as err:
        raise HTTPException(
            status_code=503,
            detail=f"No se pudo establecer conexión con la API de Envia.com: {err}"
        )
