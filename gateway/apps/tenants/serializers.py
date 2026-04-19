from rest_framework import serializers
from .models import Negocio


class NegocioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Negocio
        fields = [
            'nombre',
            'mp_access_token', 'webhook_notificacion',
            'smtp_host', 'smtp_port', 'smtp_user', 'smtp_pass', 'smtp_from',
        ]
        extra_kwargs = {
            'mp_access_token': {'write_only': True, 'required': False, 'allow_null': True},
            'smtp_pass': {'write_only': True, 'required': False, 'allow_null': True},
        }


class NegocioResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Negocio
        fields = ['id', 'nombre', 'api_key', 'webhook_notificacion',
                  'smtp_host', 'smtp_port', 'smtp_user', 'smtp_from',
                  'activo', 'created_at']
        read_only_fields = fields
