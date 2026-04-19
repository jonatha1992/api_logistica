from datetime import datetime
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .serializers import (
    QuoteRequestSerializer, CarrierListResponseSerializer,
    CarrierInfoSerializer, HealthResponseSerializer, ConfigInfoSerializer,
)
from .exceptions import EnviaAPIError
from . import client_envia, services


class WelcomeView(APIView):
    @extend_schema(tags=['General'], summary='Bienvenida')
    def get(self, request):
        return Response({
            'mensaje': 'Bienvenido al Gateway Maestro de Servicios',
            'version': '2.0.0',
            'docs': '/docs',
            'environment': settings.ENVIA_ENVIRONMENT,
        })


class StatusView(APIView):
    @extend_schema(tags=['General'], summary='Health check', responses=HealthResponseSerializer)
    def get(self, request):
        return Response({
            'status': 'operativo',
            'environment': settings.ENVIA_ENVIRONMENT,
            'timestamp': datetime.now().isoformat(),
        })


class CotizarView(APIView):
    @extend_schema(
        tags=['Cotizaciones'],
        summary='Cotizar envío',
        request=QuoteRequestSerializer,
    )
    def post(self, request):
        ser = QuoteRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            rates = client_envia.get_rates(ser.validated_data)
            return Response(rates)
        except EnviaAPIError as e:
            return Response({'detail': e.detail}, status=e.status_code)


class CarriersView(APIView):
    @extend_schema(
        tags=['Carriers'],
        summary='Listar carriers disponibles en Argentina',
        responses=CarrierListResponseSerializer,
    )
    def get(self, request):
        try:
            carriers = services.get_carriers_from_envia()
            return Response({'meta': 'carriers', 'total': len(carriers), 'data': carriers})
        except EnviaAPIError as e:
            return Response({'detail': e.detail}, status=e.status_code)


class CarrierDetailView(APIView):
    @extend_schema(
        tags=['Carriers'],
        summary='Detalle de un carrier',
        responses=CarrierInfoSerializer,
    )
    def get(self, request, carrier_name):
        try:
            carrier = services.get_carrier_by_name(carrier_name)
            if not carrier:
                return Response(
                    {'detail': f"Carrier '{carrier_name}' no encontrado"},
                    status=404,
                )
            return Response(carrier)
        except EnviaAPIError as e:
            return Response({'detail': e.detail}, status=e.status_code)


class ConfigView(APIView):
    @extend_schema(
        tags=['Configuración'],
        summary='Configuración actual de la API',
        responses=ConfigInfoSerializer,
    )
    def get(self, request):
        return Response(services.get_config_info())
