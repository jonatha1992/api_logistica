import json
import mercadopago
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from drf_spectacular.utils import extend_schema
from .models import Transaccion
from .serializers import PaymentCreateSerializer, PaymentCreateResponseSerializer


class CreatePaymentView(APIView):
    @extend_schema(
        tags=['Pagos'],
        summary='Crear preferencia de pago en MercadoPago',
        request=PaymentCreateSerializer,
        responses={201: PaymentCreateResponseSerializer},
    )
    def post(self, request):
        negocio = request.negocio

        if not negocio.mp_access_token:
            return Response(
                {'detail': 'Negocio sin token de Mercado Pago configurado. Configurarlo en /admin.'},
                status=422
            )

        ser = PaymentCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        # mp_access_token se desencripta automáticamente por EncryptedField al leer
        sdk = mercadopago.SDK(negocio.mp_access_token)

        gateway_base = settings.GATEWAY_WEBHOOK_BASE_URL
        notification_url = f"{gateway_base}/api/v1/webhooks/mercadopago/?negocio_id={negocio.id}"

        preference_payload = {
            "items": [{
                "title": data['description'],
                "quantity": 1,
                "unit_price": float(data['amount']),
                "currency_id": "ARS",
            }],
            "payer": {"email": data['customer_email']},
            "external_reference": data.get('external_reference', ''),
            "notification_url": notification_url,
            "back_urls": {
                "success": data.get('back_url_success', ''),
                "failure": data.get('back_url_failure', ''),
                "pending": data.get('back_url_pending', ''),
            },
        }

        mp_response = sdk.preference().create(preference_payload)

        if mp_response['status'] not in (200, 201):
            return Response(
                {'detail': f"Error de Mercado Pago: {mp_response.get('response', {})}"},
                status=502
            )

        preference = mp_response['response']

        transaccion = Transaccion.objects.create(
            negocio=negocio,
            preference_id=preference['id'],
            external_reference=data.get('external_reference') or None,
            amount=data['amount'],
            description=data['description'],
            customer_email=data['customer_email'],
            status='pending',
            init_point=preference['init_point'],
            metadata_json=json.dumps(data.get('metadata') or {}),
        )

        return Response({
            'init_point': preference['init_point'],
            'preference_id': preference['id'],
            'external_reference': transaccion.external_reference,
            'status': 'pending',
        }, status=201)
