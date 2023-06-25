from rest_framework import serializers


class PlaySerializer(serializers.Serializer):
    card = serializers.CharField(min_length=2, max_length=2)
