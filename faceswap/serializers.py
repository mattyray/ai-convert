from rest_framework import serializers
from .models import FaceSwapJob

class FaceSwapJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceSwapJob
        fields = ['id', 'source_image', 'target_image', 'result_image', 
                 'status', 'error_message', 'created_at', 'completed_at']
        read_only_fields = ['id', 'result_image', 'status', 'error_message', 
                           'created_at', 'completed_at']

class FaceSwapCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceSwapJob
        fields = ['source_image', 'target_image']