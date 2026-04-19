from rest_framework import serializers


class PaymentCreateSerializer(serializers.Serializer):
    amount = serializers.FloatField(min_value=0.01)
    description = serializers.CharField(max_length=500)
    customer_email = serializers.EmailField()
    external_reference = serializers.CharField(required=False, allow_blank=True, default='')
    metadata = serializers.DictField(required=False, default=dict)
    back_url_success = serializers.URLField(required=False, allow_blank=True, default='')
    back_url_failure = serializers.URLField(required=False, allow_blank=True, default='')
    back_url_pending = serializers.URLField(required=False, allow_blank=True, default='')


class PaymentCreateResponseSerializer(serializers.Serializer):
    init_point = serializers.URLField()
    preference_id = serializers.CharField()
    external_reference = serializers.CharField()
    status = serializers.CharField()
