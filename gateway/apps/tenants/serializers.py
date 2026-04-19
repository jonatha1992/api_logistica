from rest_framework import serializers
from .models import Negocio


class NegocioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Negocio
        fields = [
            # Datos del negocio
            'nombre', 'razon_social', 'cuit', 'telefono', 'direccion', 'sitio_web',
            # Identidad de marca (se inyectan en todos los templates de email)
            'nombre_comercial', 'slogan', 'icono_emoji',
            'logo_url', 'color_primario', 'color_secundario',
            'email_soporte', 'texto_footer',
            # API Keys de proveedores (write-only, se encriptan)
            'mp_access_token', 'resend_api_key',
            # SMTP (fallback para envío de emails)
            'smtp_host', 'smtp_port', 'smtp_user', 'smtp_pass', 'smtp_from',
            # Webhook
            'webhook_notificacion',
        ]
        extra_kwargs = {
            'mp_access_token': {'write_only': True, 'required': False, 'allow_null': True},
            'resend_api_key':  {'write_only': True, 'required': False, 'allow_null': True},
            'smtp_pass':       {'write_only': True, 'required': False, 'allow_null': True},
        }


class NegocioResponseSerializer(serializers.ModelSerializer):
    resend_configurado = serializers.SerializerMethodField()
    smtp_configurado   = serializers.SerializerMethodField()
    mp_configurado     = serializers.SerializerMethodField()

    class Meta:
        model = Negocio
        fields = [
            'id', 'api_key', 'activo', 'created_at',
            # Datos del negocio
            'nombre', 'razon_social', 'cuit', 'telefono', 'direccion', 'sitio_web',
            # Identidad de marca
            'nombre_comercial', 'slogan', 'icono_emoji',
            'logo_url', 'color_primario', 'color_secundario',
            'email_soporte', 'texto_footer',
            # SMTP (sin contraseña)
            'smtp_host', 'smtp_port', 'smtp_user', 'smtp_from',
            # Webhook
            'webhook_notificacion',
            # Estado de servicios (calculados)
            'resend_configurado', 'smtp_configurado', 'mp_configurado',
        ]
        read_only_fields = fields

    def get_resend_configurado(self, obj):
        return bool(obj.resend_api_key)

    def get_smtp_configurado(self, obj):
        return bool(obj.smtp_host and obj.smtp_user)

    def get_mp_configurado(self, obj):
        return bool(obj.mp_access_token)
