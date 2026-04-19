from rest_framework import serializers


class EmailSendSerializer(serializers.Serializer):
    template_slug = serializers.SlugField()
    to = serializers.EmailField()
    data = serializers.DictField(required=False, default=dict)
