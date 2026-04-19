from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from apps.tenants.throttles import PerNegocioThrottle
from .models import PlantillaEmail
from .serializers import EmailSendSerializer, EmailSendResponseSerializer
from .tasks import send_template_email


class EmailSendView(APIView):
    throttle_classes = [PerNegocioThrottle]

    @extend_schema(
        tags=['Emails'],
        summary='Enviar email usando plantilla Jinja2',
        description=(
            'Envía un email al destinatario usando una plantilla Jinja2 del negocio. '
            'Requiere que el negocio tenga SMTP configurado en /admin y que la plantilla exista. '
            'Las variables en `data` se inyectan en el asunto y cuerpo HTML de la plantilla.'
        ),
        request=EmailSendSerializer,
        responses={200: EmailSendResponseSerializer},
        examples=[
            OpenApiExample(
                'Email de bienvenida',
                value={
                    'template_slug': 'bienvenida',
                    'to': 'cliente@ejemplo.com',
                    'data': {'nombre': 'Juan García', 'link': 'https://miweb.com/activar/abc123'},
                },
                request_only=True,
            ),
            OpenApiExample(
                'Email de pago confirmado',
                value={
                    'template_slug': 'pago-confirmado',
                    'to': 'cliente@ejemplo.com',
                    'data': {'amount': 1500, 'description': 'Suscripción', 'external_reference': 'orden-001'},
                },
                request_only=True,
            ),
        ],
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
