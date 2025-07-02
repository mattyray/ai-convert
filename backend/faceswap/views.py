from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import FaceSwapJob
from .serializers import FaceSwapJobSerializer, FaceSwapCreateSerializer
from .huggingface_utils import process_face_swap
import threading


class FaceSwapCreateView(generics.CreateAPIView):
    """
    POST /api/faceswap/create/
    Upload source and target images to start face swapping
    """
    serializer_class = FaceSwapCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create job with current user
        job = serializer.save(user=request.user)
        
        # Start processing in background thread (or use Celery if available)
        def process_in_background():
            process_face_swap(job.id)
        
        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()
        
        # Return job details
        response_serializer = FaceSwapJobSerializer(job)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class FaceSwapListView(generics.ListAPIView):
    """
    GET /api/faceswap/jobs/
    List all face swap jobs for the current user
    """
    serializer_class = FaceSwapJobSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FaceSwapJob.objects.filter(user=self.request.user)


class FaceSwapDetailView(generics.RetrieveAPIView):
    """
    GET /api/faceswap/jobs/{id}/
    Get details of a specific face swap job
    """
    serializer_class = FaceSwapJobSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FaceSwapJob.objects.filter(user=self.request.user)


class FaceSwapStatusView(APIView):
    """
    GET /api/faceswap/status/{id}/
    Quick status check for a face swap job
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, job_id):
        job = get_object_or_404(FaceSwapJob, id=job_id, user=request.user)
        return Response({
            'id': job.id,
            'status': job.status,
            'error_message': job.error_message,
            'result_image': job.result_image.url if job.result_image else None,
            'created_at': job.created_at,
            'completed_at': job.completed_at
        })