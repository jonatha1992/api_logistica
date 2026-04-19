from rest_framework import serializers


# ── Request serializers ───────────────────────────────────────────────────────

class SimpleAddressSerializer(serializers.Serializer):
    street = serializers.CharField()
    number = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField(max_length=10)
    postal_code = serializers.CharField()
    country_code = serializers.CharField(max_length=5)
    contact_name = serializers.CharField()
    contact_email = serializers.EmailField()
    contact_phone = serializers.CharField()


class SimpleParcelSerializer(serializers.Serializer):
    weight = serializers.FloatField()
    height = serializers.FloatField()
    width = serializers.FloatField()
    length = serializers.FloatField()
    content = serializers.CharField()


class QuoteRequestSerializer(serializers.Serializer):
    origin = SimpleAddressSerializer()
    destination = SimpleAddressSerializer()
    parcels = SimpleParcelSerializer(many=True)
    carrier = serializers.CharField(required=False, allow_null=True, default=None)
    currency = serializers.CharField(default='ARS')


# ── Response serializers ──────────────────────────────────────────────────────

class CarrierInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    carrier_code = serializers.CharField()
    description = serializers.CharField()
    active = serializers.BooleanField()
    country = serializers.CharField()
    category = serializers.CharField()


class CarrierListResponseSerializer(serializers.Serializer):
    meta = serializers.CharField()
    total = serializers.IntegerField()
    data = CarrierInfoSerializer(many=True)


class HealthResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    environment = serializers.CharField()
    timestamp = serializers.CharField()


class ConfigInfoSerializer(serializers.Serializer):
    environment = serializers.CharField()
    api_url = serializers.CharField()
    token_configured = serializers.BooleanField()
    available_environments = serializers.ListField(child=serializers.CharField())
