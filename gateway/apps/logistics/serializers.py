from rest_framework import serializers


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
