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
        
# Add this debug view to your faceswap/views.py

class DebugGradioAPIView(APIView):
    """
    Debug endpoint to test Gradio Space connectivity
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            from .huggingface_utils import HUGGINGFACE_SPACE_URL
            import requests
            
            results = {}
            
            # Test 1: Check if the space is running
            try:
                response = requests.get(HUGGINGFACE_SPACE_URL, timeout=10)
                results['space_status'] = f"HTTP {response.status_code}"
                results['space_accessible'] = response.status_code == 200
            except Exception as e:
                results['space_status'] = f"Error: {str(e)}"
                results['space_accessible'] = False
            
            # Test 2: Try to get API info using gradio_client
            try:
                from gradio_client import Client
                client = Client(HUGGINGFACE_SPACE_URL)
                api_info = client.view_api(all_endpoints=True)
                results['gradio_client_success'] = True
                results['api_info'] = str(api_info)
            except Exception as e:
                results['gradio_client_success'] = False
                results['gradio_client_error'] = str(e)
            
            # Test 3: Try common Gradio endpoints
            endpoints_to_test = [
                '/api/predict',
                '/run/predict', 
                '/predict',
                '/api',
                '/info',
                '/app_info'
            ]
            
            results['endpoint_tests'] = {}
            for endpoint in endpoints_to_test:
                try:
                    url = f"{HUGGINGFACE_SPACE_URL}{endpoint}"
                    response = requests.get(url, timeout=5)
                    results['endpoint_tests'][endpoint] = {
                        'status': response.status_code,
                        'content_type': response.headers.get('content-type', 'unknown'),
                        'content_preview': response.text[:200] if response.text else 'No content'
                    }
                except Exception as e:
                    results['endpoint_tests'][endpoint] = {
                        'error': str(e)
                    }
            
            # Test 4: Check if it's a Gradio 4 or 5 app
            try:
                response = requests.get(f"{HUGGINGFACE_SPACE_URL}/info", timeout=5)
                if response.status_code == 200:
                    results['gradio_info'] = response.json()
            except:
                pass
                
            return Response({
                'space_url': HUGGINGFACE_SPACE_URL,
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
            from .huggingface_utils import HUGGINGFACE_SPACE_URL, HUGGINGFACE_API_TOKEN
            import requests
            from gradio_client import Client
            
            results = {}
            
            # Test 1: Basic connectivity
            try:
                print("🔍 Testing basic connectivity...")
                response = requests.get(HUGGINGFACE_SPACE_URL, timeout=10)
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
            
            # Test 2: Authentication test
            try:
                print("🔑 Testing authentication...")
                headers = {}
                if HUGGINGFACE_API_TOKEN:
                    headers['Authorization'] = f'Bearer {HUGGINGFACE_API_TOKEN}'
                
                response = requests.get(
                    f"{HUGGINGFACE_SPACE_URL}/info", 
                    headers=headers,
                    timeout=10
                )
                results['authentication'] = {
                    'status': response.status_code,
                    'token_provided': bool(HUGGINGFACE_API_TOKEN),
                    'token_length': len(HUGGINGFACE_API_TOKEN) if HUGGINGFACE_API_TOKEN else 0,
                    'response': response.text[:200] if response.text else 'No content'
                }
            except Exception as e:
                results['authentication'] = {
                    'error': str(e),
                    'token_provided': bool(HUGGINGFACE_API_TOKEN)
                }
            
            # Test 3: Gradio API endpoints
            api_endpoints = [
                '/api/predict',
                '/run/predict',
                '/api/queue/push',
                '/info',
                '/config'
            ]
            
            results['api_endpoints'] = {}
            for endpoint in api_endpoints:
                try:
                    headers = {}
                    if HUGGINGFACE_API_TOKEN:
                        headers['Authorization'] = f'Bearer {HUGGINGFACE_API_TOKEN}'
                    
                    response = requests.get(
                        f"{HUGGINGFACE_SPACE_URL}{endpoint}",
                        headers=headers,
                        timeout=5
                    )
                    results['api_endpoints'][endpoint] = {
                        'status': response.status_code,
                        'content_type': response.headers.get('content-type', 'unknown'),
                        'size': len(response.content)
                    }
                except Exception as e:
                    results['api_endpoints'][endpoint] = {'error': str(e)}
            
            # Test 4: Gradio Client connection
            try:
                print("🎭 Testing Gradio Client...")
                client = Client(HUGGINGFACE_SPACE_URL, hf_token=HUGGINGFACE_API_TOKEN)
                
                # Try to get API info
                api_info = client.view_api(return_format="dict")
                results['gradio_client'] = {
                    'connection': 'success',
                    'api_endpoints': list(api_info.keys()) if isinstance(api_info, dict) else 'Not a dict',
                    'endpoint_count': len(api_info) if isinstance(api_info, dict) else 0
                }
                
                # Check if our specific endpoint exists
                if 'process_images' in str(api_info):
                    results['gradio_client']['process_images_available'] = True
                else:
                    results['gradio_client']['process_images_available'] = False
                    results['gradio_client']['available_endpoints'] = str(api_info)[:500]
                
            except Exception as e:
                results['gradio_client'] = {
                    'connection': 'failed',
                    'error': str(e)
                }
            
            # Test 5: Direct API test with sample data
            try:
                print("🧪 Testing direct API call...")
                headers = {'Content-Type': 'application/json'}
                if HUGGINGFACE_API_TOKEN:
                    headers['Authorization'] = f'Bearer {HUGGINGFACE_API_TOKEN}'
                
                test_payload = {
                    "data": [
                        "https://res.cloudinary.com/dddye9wli/image/upload/v1749856308/selfie2_sukvhg.jpg",
                        "https://res.cloudinary.com/dddye9wli/image/upload/v1749857225/elvisnotsinging_twnnta.png"
                    ],
                    "fn_index": 0
                }
                
                response = requests.post(
                    f"{HUGGINGFACE_SPACE_URL}/api/predict",
                    json=test_payload,
                    headers=headers,
                    timeout=60
                )
                
                results['direct_api_test'] = {
                    'status': response.status_code,
                    'success': response.status_code == 200,
                    'response_preview': response.text[:300] if response.text else 'No content',
                    'headers': dict(response.headers)
                }
                
                if response.status_code == 200:
                    try:
                        response_json = response.json()
                        results['direct_api_test']['response_type'] = type(response_json).__name__
                        results['direct_api_test']['has_data'] = 'data' in response_json
                    except:
                        results['direct_api_test']['response_type'] = 'not_json'
                
            except Exception as e:
                results['direct_api_test'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            # Summary and recommendations
            recommendations = []
            
            if not results.get('basic_connectivity', {}).get('accessible'):
                recommendations.append("❌ Space is not accessible - check if it's running")
            
            if not HUGGINGFACE_API_TOKEN:
                recommendations.append("🔑 No API token provided - add HUGGINGFACE_API_TOKEN")
            
            if results.get('gradio_client', {}).get('connection') == 'failed':
                recommendations.append("🎭 Gradio client connection failed - try direct API approach")
            
            if not results.get('gradio_client', {}).get('process_images_available'):
                recommendations.append("📋 process_images endpoint not found - check your Gradio app")
            
            if results.get('direct_api_test', {}).get('status') == 429:
                recommendations.append("⚠️ Rate limited on direct API - space may be overwhelmed")
            
            if not recommendations:
                recommendations.append("✅ All tests passed - connection should work!")
            
            return Response({
                'space_url': HUGGINGFACE_SPACE_URL,
                'token_configured': bool(HUGGINGFACE_API_TOKEN),
                'test_results': results,
                'recommendations': recommendations,
                'next_steps': [
                    "1. Ensure your HuggingFace Space is running and accessible",
                    "2. Verify your HUGGINGFACE_API_TOKEN is correct",
                    "3. Check that your Gradio app has the 'process_images' function",
                    "4. Try the enhanced FaceFusionClient with multiple fallback methods",
                    "5. Monitor your Space's logs for errors"
                ]
            })
            
        except Exception as e:
            return Response({
                'error': f'Debug failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)