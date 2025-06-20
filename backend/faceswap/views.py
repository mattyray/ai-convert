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

class DebugGradioAPIView(APIView):
    """
    Debug endpoint to test Gradio Space connectivity
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            from .huggingface_utils import HUGGINGFACE_SPACE_NAME, HUGGINGFACE_API_TOKEN
            from gradio_client import Client
            import requests
            
            results = {}
            
            # Build the .hf.space URL for testing
            space_parts = HUGGINGFACE_SPACE_NAME.split('/')
            if len(space_parts) == 2:
                direct_url = f"https://{space_parts[0]}-{space_parts[1]}.hf.space"
            else:
                direct_url = "Invalid space name format"
            
            results['configuration'] = {
                'space_name': HUGGINGFACE_SPACE_NAME,
                'direct_url': direct_url,
                'token_configured': bool(HUGGINGFACE_API_TOKEN),
                'token_length': len(HUGGINGFACE_API_TOKEN) if HUGGINGFACE_API_TOKEN else 0
            }
            
            # Test 1: Check if the space is accessible
            try:
                response = requests.get(direct_url, timeout=10)
                results['space_accessibility'] = {
                    'status': f"HTTP {response.status_code}",
                    'accessible': response.status_code == 200,
                    'response_size': len(response.content)
                }
            except Exception as e:
                results['space_accessibility'] = {
                    'status': f"Error: {str(e)}",
                    'accessible': False
                }
            
            # Test 2: Try Gradio client connection
            try:
                client = Client(HUGGINGFACE_SPACE_NAME, hf_token=HUGGINGFACE_API_TOKEN)
                api_info = client.view_api(return_format="dict")
                results['gradio_client'] = {
                    'connection': 'success',
                    'api_endpoints': list(api_info.keys()) if isinstance(api_info, dict) else 'Not a dict',
                    'endpoint_count': len(api_info) if isinstance(api_info, dict) else 0,
                    'has_process_images': '/process_images' in str(api_info)
                }
            except Exception as e:
                results['gradio_client'] = {
                    'connection': 'failed',
                    'error': str(e)
                }
                
            return Response({
                'space_name': HUGGINGFACE_SPACE_NAME,
                'debug_results': results
            })
            
        except Exception as e:
            return Response({
                'error': f'Debug failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HuggingFaceDebugView(APIView):
    """
    Comprehensive debug endpoint to test HuggingFace Space connectivity
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            from .huggingface_utils import HUGGINGFACE_SPACE_NAME, HUGGINGFACE_API_TOKEN
            from gradio_client import Client
            import requests
            
            results = {}
            
            # Build direct URL from space name
            space_parts = HUGGINGFACE_SPACE_NAME.split('/')
            if len(space_parts) == 2:
                direct_url = f"https://{space_parts[0]}-{space_parts[1]}.hf.space"
            else:
                return Response({
                    'error': f'Invalid space name format: {HUGGINGFACE_SPACE_NAME}. Expected: owner/space-name'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            results['configuration'] = {
                'space_name': HUGGINGFACE_SPACE_NAME,
                'direct_url': direct_url,
                'token_configured': bool(HUGGINGFACE_API_TOKEN)
            }
            
            # Test 1: Basic connectivity
            try:
                print("🔍 Testing basic connectivity...")
                response = requests.get(direct_url, timeout=10)
                results['basic_connectivity'] = {
                    'status': f"HTTP {response.status_code}",
                    'accessible': response.status_code == 200,
                    'response_size': len(response.content)
                }
            except Exception as e:
                results['basic_connectivity'] = {
                    'status': f"Error: {str(e)}",
                    'accessible': False
                }
            
            # Test 2: Gradio Client connection
            try:
                print("🎭 Testing Gradio Client...")
                client = Client(HUGGINGFACE_SPACE_NAME, hf_token=HUGGINGFACE_API_TOKEN)
                
                # Try to get API info
                api_info = client.view_api(return_format="dict")
                results['gradio_client'] = {
                    'connection': 'success',
                    'api_endpoints': list(api_info.keys()) if isinstance(api_info, dict) else 'Not a dict',
                    'endpoint_count': len(api_info) if isinstance(api_info, dict) else 0
                }
                
                # Check if our specific endpoint exists
                if '/process_images' in str(api_info):
                    results['gradio_client']['process_images_available'] = True
                else:
                    results['gradio_client']['process_images_available'] = False
                    results['gradio_client']['available_endpoints'] = str(api_info)[:500]
                
            except Exception as e:
                results['gradio_client'] = {
                    'connection': 'failed',
                    'error': str(e)
                }
            
            # Test 3: Try actual FaceFusion client
            try:
                print("🧪 Testing FaceFusion client...")
                from .huggingface_utils import FaceFusionClient
                client = FaceFusionClient()
                
                # Test setup
                setup_result = client.setup_facefusion()
                results['facefusion_client'] = {
                    'setup': 'success',
                    'setup_result': setup_result
                }
                
            except Exception as e:
                results['facefusion_client'] = {
                    'setup': 'failed',
                    'error': str(e)
                }
            
            # Summary and recommendations
            recommendations = []
            
            if not results.get('basic_connectivity', {}).get('accessible'):
                recommendations.append("❌ Space is not accessible - check if it's running")
            
            if not HUGGINGFACE_API_TOKEN:
                recommendations.append("🔑 No API token provided - add HUGGINGFACE_API_TOKEN")
            
            if results.get('gradio_client', {}).get('connection') == 'failed':
                recommendations.append("🎭 Gradio client connection failed - check space name and token")
            
            if not results.get('gradio_client', {}).get('process_images_available'):
                recommendations.append("📋 process_images endpoint not found - check your Gradio app")
            
            if not recommendations:
                recommendations.append("✅ All tests passed - connection should work!")
            
            return Response({
                'space_name': HUGGINGFACE_SPACE_NAME,
                'direct_url': direct_url,
                'token_configured': bool(HUGGINGFACE_API_TOKEN),
                'test_results': results,
                'recommendations': recommendations
            })
            
        except Exception as e:
            return Response({
                'error': f'Debug failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TestGradioConnectionView(APIView):
    """Test Gradio client connection with environment variables"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            from django.conf import settings
            from .huggingface_utils import FaceFusionClient, HUGGINGFACE_SPACE_NAME, HUGGINGFACE_API_TOKEN
            
            # Debug environment variables
            debug_info = {
                'space_name_from_settings': getattr(settings, 'HUGGINGFACE_SPACE_NAME', 'NOT_SET'),
                'api_token_configured': bool(getattr(settings, 'HUGGINGFACE_API_TOKEN', None)),
                'space_name_from_utils': HUGGINGFACE_SPACE_NAME,
                'api_token_length': len(HUGGINGFACE_API_TOKEN) if HUGGINGFACE_API_TOKEN else 0
            }
            
            client = FaceFusionClient()
            
            # Test 1: Create client
            gradio_client = client.get_client()
            
            # Test 2: Try setup
            setup_result = client.setup_facefusion()
            
            return Response({
                'status': 'success',
                'debug_info': debug_info,
                'setup_result': setup_result,
                'message': 'Gradio client connection successful!'
            })
            
        except Exception as e:
            # Make sure debug_info is available in the error case
            debug_info = {}
            try:
                from django.conf import settings
                from .huggingface_utils import HUGGINGFACE_SPACE_NAME, HUGGINGFACE_API_TOKEN
                debug_info = {
                    'space_name_from_settings': getattr(settings, 'HUGGINGFACE_SPACE_NAME', 'NOT_SET'),
                    'api_token_configured': bool(getattr(settings, 'HUGGINGFACE_API_TOKEN', None)),
                    'space_name_from_utils': HUGGINGFACE_SPACE_NAME,
                    'api_token_length': len(HUGGINGFACE_API_TOKEN) if HUGGINGFACE_API_TOKEN else 0
                }
            except Exception:
                pass
                
            return Response({
                'status': 'error',
                'debug_info': debug_info,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)