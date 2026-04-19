from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Negocio
from .serializers import NegocioCreateSerializer, NegocioResponseSerializer


class NegocioListCreateView(APIView):
    @extend_schema(
        tags=['Tenants'],
        summary='Listar negocios',
        responses=NegocioResponseSerializer(many=True),
    )
    def get(self, request):
        negocios = Negocio.objects.all()
        return Response(NegocioResponseSerializer(negocios, many=True).data)

    @extend_schema(
        tags=['Tenants'],
        summary='Crear negocio (genera api_key automáticamente)',
        request=NegocioCreateSerializer,
        responses={201: NegocioResponseSerializer},
    )
    def post(self, request):
        ser = NegocioCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        negocio = ser.save()
        return Response(NegocioResponseSerializer(negocio).data, status=201)


class NegocioDetailView(APIView):
    def _get_negocio(self, pk):
        try:
            return Negocio.objects.get(pk=pk)
        except Negocio.DoesNotExist:
            return None

    @extend_schema(
        tags=['Tenants'],
        summary='Detalle de un negocio',
        responses=NegocioResponseSerializer,
    )
    def get(self, request, pk):
        negocio = self._get_negocio(pk)
        if not negocio:
            return Response({'detail': 'Negocio no encontrado'}, status=404)
        return Response(NegocioResponseSerializer(negocio).data)

    @extend_schema(
        tags=['Tenants'],
        summary='Actualizar negocio',
        request=NegocioCreateSerializer,
        responses=NegocioResponseSerializer,
    )
    def patch(self, request, pk):
        negocio = self._get_negocio(pk)
        if not negocio:
            return Response({'detail': 'Negocio no encontrado'}, status=404)
        ser = NegocioCreateSerializer(negocio, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        negocio = ser.save()
        return Response(NegocioResponseSerializer(negocio).data)

    @extend_schema(tags=['Tenants'], summary='Eliminar negocio')
    def delete(self, request, pk):
        negocio = self._get_negocio(pk)
        if not negocio:
            return Response({'detail': 'Negocio no encontrado'}, status=404)
        negocio.delete()
        return Response(status=204)
