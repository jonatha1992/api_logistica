import mercadopago
import httpx
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.tenants.models import Negocio
from apps.payments.models import Transaccion
from apps.emails.tasks import send_payment_confirmation_email


class MercadoPagoWebhookView(APIView):
    def post(self, request):
        negocio_id = request.GET.get('negocio_id')
        if not negocio_id:
            return Response({'status': 'missing_negocio_id'}, status=400)

        body = request.data
        if body.get('type') != 'payment':
            return Response({'status': 'ignored', 'type': body.get('type')})

        payment_id = body.get('data', {}).get('id')
        if not payment_id:
            return Response({'status': 'no_payment_id'})

        try:
            negocio = Negocio.objects.get(id=negocio_id, activo=True)
        except Negocio.DoesNotExist:
            return Response({'status': 'negocio_not_found'}, status=404)

        if not negocio.mp_access_token:
            return Response({'status': 'no_mp_token'}, status=422)

        # mp_access_token se desencripta automáticamente por EncryptedField
        sdk = mercadopago.SDK(negocio.mp_access_token)
        mp_response = sdk.payment().get(payment_id)

        if mp_response['status'] != 200:
            return Response({'status': 'mp_error'}, status=502)

        detail = mp_response['response']
        preference_id = detail.get('preference_id')
        mp_status = detail.get('status')

        try:
            t = Transaccion.objects.get(preference_id=preference_id, negocio=negocio)
        except Transaccion.DoesNotExist:
            return Response({'status': 'transaction_not_found', 'preference_id': preference_id})

        t.status = mp_status
        t.payment_id = str(payment_id)
        t.save()

        if mp_status == 'approved':
            # Email de confirmación asíncrono
            send_payment_confirmation_email.delay(t.id, negocio.id)

            # Notificación al sistema del negocio (webhook de salida)
            if negocio.webhook_notificacion:
                try:
                    httpx.post(
                        negocio.webhook_notificacion,
                        json={
                            'event': 'payment.approved',
                            'payment_id': str(payment_id),
                            'preference_id': preference_id,
                            'external_reference': t.external_reference,
                            'amount': t.amount,
                            'customer_email': t.customer_email,
                        },
                        timeout=5.0
                    )
                except Exception:
                    pass

        return Response({
            'status': 'processed',
            'payment_status': mp_status,
            'payment_id': str(payment_id),
        })
