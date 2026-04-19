from datetime import datetime
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import QuoteRequestSerializer
from .exceptions import EnviaAPIError
from . import client_envia, services


class WelcomeView(APIView):
    def get(self, request):
        return Response({
            'mensaje': 'Bienvenido al Gateway Maestro de Servicios',
            'version': '2.0.0',
            'docs': '/admin',
            'environment': settings.ENVIA_ENVIRONMENT,
        })


class StatusView(APIView):
    def get(self, request):
        return Response({
            'status': 'operativo',
            'environment': settings.ENVIA_ENVIRONMENT,
            'timestamp': datetime.now().isoformat(),
        })


class CotizarView(APIView):
    def post(self, request):
        ser = QuoteRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            rates = client_envia.get_rates(ser.validated_data)
            return Response(rates)
        except EnviaAPIError as e:
            return Response({'detail': e.detail}, status=e.status_code)


class CarriersView(APIView):
    def get(self, request):
        try:
            carriers = services.get_carriers_from_envia()
            return Response({'meta': 'carriers', 'total': len(carriers), 'data': carriers})
        except EnviaAPIError as e:
            return Response({'detail': e.detail}, status=e.status_code)


class CarrierDetailView(APIView):
    def get(self, request, carrier_name):
        try:
            carrier = services.get_carrier_by_name(carrier_name)
            if not carrier:
                return Response(
                    {'detail': f"Carrier '{carrier_name}' no encontrado"},
                    status=404
                )
            return Response(carrier)
        except EnviaAPIError as e:
            return Response({'detail': e.detail}, status=e.status_code)


class ConfigView(APIView):
    def get(self, request):
        return Response(services.get_config_info())
