from rest_framework import serializers
from .models import GeneratedImage

class GeneratedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedImage
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'user']
