from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    negocio_id = serializers.IntegerField(source='negocio.id', allow_null=True, read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'negocio_id', 'endpoint', 'method', 'status_code', 'error_message', 'created_at']


class AuditLogListView(APIView):
    @extend_schema(
        tags=['Auditoría'],
        summary='Listar logs de auditoría',
        parameters=[
            OpenApiParameter('negocio_id', int, description='Filtrar por negocio', required=False),
            OpenApiParameter('endpoint', str, description='Filtrar por endpoint (contiene)', required=False),
            OpenApiParameter('status_code', int, description='Filtrar por código HTTP', required=False),
            OpenApiParameter('limit', int, description='Máximo registros a devolver (default 100)', required=False),
        ],
        responses=AuditLogSerializer(many=True),
    )
    def get(self, request):
        qs = AuditLog.objects.select_related('negocio').all()

        negocio_id = request.query_params.get('negocio_id')
        if negocio_id:
            qs = qs.filter(negocio_id=negocio_id)

        endpoint = request.query_params.get('endpoint')
        if endpoint:
            qs = qs.filter(endpoint__icontains=endpoint)

        status_code = request.query_params.get('status_code')
        if status_code:
            qs = qs.filter(status_code=status_code)

        limit = int(request.query_params.get('limit', 100))
        qs = qs[:limit]

        return Response(AuditLogSerializer(qs, many=True).data)
