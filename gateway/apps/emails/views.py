from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.tenants.throttles import PerNegocioThrottle
from .models import PlantillaEmail
from .serializers import EmailSendSerializer, EmailSendResponseSerializer
from .tasks import send_template_email


class EmailSendView(APIView):
    throttle_classes = [PerNegocioThrottle]

    @extend_schema(
        tags=['Emails'],
        summary='Enviar email usando plantilla Jinja2',
        request=EmailSendSerializer,
        responses={200: EmailSendResponseSerializer},
    )
    def post(self, request):
        negocio = request.negocio

        if not negocio.smtp_host:
            return Response(
                {'detail': 'Negocio sin configuración SMTP. Configurarlo en /admin.'},
                status=422
            )

        ser = EmailSendSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        if not PlantillaEmail.objects.filter(
            negocio=negocio,
            slug=data['template_slug'],
            activa=True
        ).exists():
            return Response(
                {'detail': f"Plantilla '{data['template_slug']}' no encontrada para este negocio"},
                status=404
            )

        send_template_email.delay(
            negocio_id=negocio.id,
            template_slug=data['template_slug'],
            to_email=data['to'],
            data=data.get('data') or {},
        )

        return Response({
            'status': 'queued',
            'message': f"Correo a {data['to']} encolado para envío asíncrono",
        })
