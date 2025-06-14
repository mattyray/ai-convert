from rest_framework import generics, status
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
    
# Add this to your existing faceswap/views.py file

class FaceSwapTestURLView(APIView):
    """
    POST /api/faceswap/test-url/
    Test face swapping with direct URLs (for testing with Cloudinary)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        source_url = request.data.get('source_url')
        target_url = request.data.get('target_url')
        
        if not source_url or not target_url:
            return Response({
                'error': 'Both source_url and target_url are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from .huggingface_utils import FaceFusionClient
            client = FaceFusionClient()
            
            # Create a simple mock object with url property
            class MockImageField:
                def __init__(self, url):
                    self.url = url
            
            source_mock = MockImageField(source_url)
            target_mock = MockImageField(target_url)
            
            # Test the face swap
            result_data = client.swap_faces(source_mock, target_mock)
            
            # Return base64 encoded result for testing
            import base64
            result_b64 = base64.b64encode(result_data).decode('utf-8')
            
            return Response({
                'status': 'success',
                'message': 'Face swap completed successfully',
                'result_size': len(result_data),
                'result_preview': f"data:image/jpeg;base64,{result_b64[:100]}..."  # First 100 chars
            })
            
        except Exception as e:
            return Response({
                'error': f'Face swap failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)