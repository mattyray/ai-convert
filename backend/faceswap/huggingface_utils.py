# faceswap/huggingface_utils.py - IMPROVED VERSION

import requests
import time
from django.conf import settings
from django.core.files.base import ContentFile
import tempfile
import os
import base64
from gradio_client import Client
import random
import threading
import json

# 🔗 HuggingFace Space Configuration - matches environment variables
HUGGINGFACE_SPACE_NAME = getattr(settings, 'HUGGINGFACE_SPACE_NAME', 
                                'mnraynor90/facefusionfastapi-private')

# 🔑 HuggingFace Authentication Token (from environment)
HUGGINGFACE_API_TOKEN = getattr(settings, 'HUGGINGFACE_API_TOKEN', None)

# Export these for use in views
__all__ = ['FaceFusionClient', 'process_face_swap', 'HUGGINGFACE_SPACE_NAME', 'HUGGINGFACE_API_TOKEN']

def validate_huggingface_config():
    """Validate HuggingFace configuration for security and correctness"""
    issues = []
    
    # Check space name format
    if not HUGGINGFACE_SPACE_NAME or '/' not in HUGGINGFACE_SPACE_NAME:
        issues.append("Invalid HUGGINGFACE_SPACE_NAME format. Expected: 'owner/space-name'")
    
    # Check API token
    if not HUGGINGFACE_API_TOKEN or HUGGINGFACE_API_TOKEN in ['dummy', 'your_token_here']:
        issues.append("Missing or invalid HUGGINGFACE_API_TOKEN. Private spaces require authentication.")
    elif not HUGGINGFACE_API_TOKEN.startswith('hf_'):
        issues.append("Invalid HUGGINGFACE_API_TOKEN format. HuggingFace tokens should start with 'hf_'")
    elif len(HUGGINGFACE_API_TOKEN) < 30:
        issues.append("HUGGINGFACE_API_TOKEN appears too short to be valid")
    
    return issues

class FaceFusionClient:
    """
    IMPROVED: Proper Gradio Client for private space with enhanced authentication and validation
    """
    
    def __init__(self):
        self.client = None
        self.space_name = HUGGINGFACE_SPACE_NAME
        self._validate_config()
        
    def _validate_config(self):
        """Validate configuration before attempting connection"""
        issues = validate_huggingface_config()
        if issues:
            raise Exception(f"HuggingFace configuration issues: {'; '.join(issues)}")
    
    def get_client(self):
        """Get authenticated Gradio client for private space with enhanced error handling"""
        if self.client is None:
            try:
                print(f"🔌 Creating authenticated Gradio client for: {self.space_name}")
                print(f"🔑 Token length: {len(HUGGINGFACE_API_TOKEN)} chars")
                
                # Connect to private space with authentication
                self.client = Client(
                    self.space_name,
                    hf_token=HUGGINGFACE_API_TOKEN
                )
                
                print("✅ Authenticated Gradio client created successfully")
                
                # Test the connection by getting API info
                try:
                    api_info = self.client.view_api()
                    print(f"📋 API connection successful")
                    
                    # Check for required endpoints
                    api_str = str(api_info)
                    if '/process_images' in api_str:
                        print("✅ Required /process_images endpoint found")
                    else:
                        print(f"⚠️ /process_images endpoint not found. Available: {api_str[:200]}...")
                        
                except Exception as e:
                    print(f"⚠️ Could not verify API endpoints: {e}")
                
            except Exception as e:
                error_msg = str(e).lower()
                if 'authentication' in error_msg or 'token' in error_msg or 'unauthorized' in error_msg:
                    raise Exception(f"❌ Authentication failed: Invalid or expired HuggingFace API token. Please check your HUGGINGFACE_API_TOKEN")
                elif 'not found' in error_msg or '404' in error_msg:
                    raise Exception(f"❌ Space not found: '{self.space_name}' does not exist or is not accessible")
                elif 'rate limit' in error_msg or 'too many' in error_msg:
                    raise Exception(f"❌ Rate limited: Too many requests to HuggingFace. Please try again later")
                else:
                    raise Exception(f"❌ Failed to create Gradio client: {e}")
                
        return self.client
    
    def test_connection(self):
        """Test connection without performing operations"""
        try:
            client = self.get_client()
            api_info = client.view_api()
            return {
                'status': 'success',
                'space_name': self.space_name,
                'token_valid': True,
                'api_endpoints_available': '/process_images' in str(api_info)
            }
        except Exception as e:
            return {
                'status': 'failed',
                'space_name': self.space_name,
                'token_valid': False,
                'error': str(e)
            }
    
    def get_image_url(self, image_field):
        """Convert Django ImageField to accessible URL"""
        try:
            if hasattr(image_field, 'url'):
                image_url = image_field.url
                
                if image_url.startswith('http'):
                    return image_url
                
                if image_url.startswith('/') and hasattr(image_field, 'name'):
                    try:
                        import cloudinary.utils
                        cloudinary_url = cloudinary.utils.cloudinary_url(image_field.name)[0]
                        print(f"✅ Using Cloudinary URL: {cloudinary_url}")
                        return cloudinary_url
                    except Exception as e:
                        print(f"⚠️ Cloudinary failed: {e}")
                        base_url = getattr(settings, 'BASE_URL', 'http://127.0.0.1:8002')
                        return f"{base_url}{image_url}"
                
                return image_url
            else:
                raise Exception("Invalid image field")
        except Exception as e:
            raise Exception(f"Failed to get image URL: {str(e)}")
    
    def setup_facefusion(self):
        """Setup FaceFusion before processing with retry logic"""
        max_retries = 2
        for attempt in range(max_retries):
            try:
                print(f"🔧 Setting up FaceFusion (attempt {attempt + 1}/{max_retries})...")
                client = self.get_client()
                
                result = client.predict(api_name="/setup_facefusion")
                print(f"✅ Setup complete: {result}")
                return result
                
            except Exception as e:
                print(f"❌ Setup attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    self.client = None  # Reset client for retry
                    continue
                raise e
    
    def swap_faces(self, source_image_field, target_image_field, max_retries=3):
        """
        IMPROVED: Use proper Gradio client with enhanced error handling and validation
        """
        # Get URLs
        source_url = self.get_image_url(source_image_field)
        target_url = self.get_image_url(target_image_field)
        
        print(f"🔄 Starting face swap with Gradio client")
        print(f"  Source: {source_url[:80]}...")
        print(f"  Target: {target_url[:80]}...")
        
        for attempt in range(max_retries):
            try:
                print(f"🎭 Face swap attempt {attempt + 1}/{max_retries}")
                
                client = self.get_client()
                
                # Optional: Setup FaceFusion first
                try:
                    self.setup_facefusion()
                except Exception as setup_error:
                    print(f"⚠️ Setup failed: {setup_error}, continuing anyway...")
                
                # Call the correct API endpoint with proper parameters
                result = client.predict(
                    source_url=source_url,  # 👤 Source Image URL (Face to transfer)
                    target_url=target_url,  # 🎯 Target Image URL (Body/scene)
                    api_name="/process_images"
                )
                
                print(f"📋 Gradio result: {type(result)} - {result}")
                
                if not result or len(result) < 2:
                    raise Exception(f"Invalid result format: {result}")
                
                result_filepath = result[0]  # Image file path
                status_message = result[1]   # Status message
                
                print(f"📋 Status: {status_message}")
                print(f"📁 Result file: {result_filepath}")
                
                # Handle the result file path
                if hasattr(result_filepath, 'save'):  # PIL Image
                    print("✅ Got PIL Image, converting to bytes")
                    import io
                    img_buffer = io.BytesIO()
                    result_filepath.save(img_buffer, format='JPEG', quality=90)
                    return img_buffer.getvalue()
                    
                elif isinstance(result_filepath, str) and os.path.exists(result_filepath):  # File path
                    print(f"✅ Got file path: {result_filepath}")
                    with open(result_filepath, 'rb') as f:
                        return f.read()
                        
                elif isinstance(result_filepath, dict):  # Gradio file object
                    if 'path' in result_filepath and os.path.exists(result_filepath['path']):
                        print(f"✅ Got Gradio file object: {result_filepath['path']}")
                        with open(result_filepath['path'], 'rb') as f:
                            return f.read()
                    elif 'url' in result_filepath:
                        print(f"✅ Got URL from Gradio: {result_filepath['url']}")
                        # Download from URL
                        response = requests.get(result_filepath['url'], timeout=60)
                        response.raise_for_status()
                        return response.content
                        
                else:
                    raise Exception(f"Unexpected result format: {type(result_filepath)} - {result_filepath}")
                    
            except Exception as e:
                error_msg = str(e).lower()
                print(f"❌ Face swap attempt {attempt + 1} failed: {e}")
                
                # Handle specific error types
                if 'authentication' in error_msg or 'unauthorized' in error_msg:
                    raise Exception("Authentication failed. Please check your HuggingFace API token.")
                elif 'slow down' in error_msg or 'too many' in error_msg or 'rate limit' in error_msg:
                    print("🚨 Rate limited - resetting client")
                    self.client = None  # Reset client
                    
                    if attempt < max_retries - 1:
                        delay = (2 ** attempt) * 3 + random.uniform(0, 3)
                        print(f"⏳ Waiting {delay:.1f}s...")
                        time.sleep(delay)
                        continue
                    else:
                        raise Exception("Rate limited after all retries")
                
                elif attempt < max_retries - 1:
                    delay = 5 + random.uniform(0, 2)
                    print(f"⏳ Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                else:
                    break
        
        raise Exception(f"All face swap attempts failed")

def process_face_swap(job_id):
    """
    Process a face swap job using the improved Gradio client
    """
    from .models import FaceSwapJob
    from django.utils import timezone
    
    try:
        job = FaceSwapJob.objects.get(id=job_id)
        job.status = 'processing'
        job.save()
        
        print(f"🚀 Processing face swap job {job_id} with improved Gradio client")
        
        # Initialize the client
        client = FaceFusionClient()
        
        # Test connection first
        connection_test = client.test_connection()
        if connection_test['status'] != 'success':
            raise Exception(f"Connection test failed: {connection_test['error']}")
        
        # Perform face swap
        result_image_data = client.swap_faces(job.source_image, job.target_image)
        
        # Save result
        result_filename = f"faceswap_result_{job.id}_{int(time.time())}.jpg"
        result_file = ContentFile(result_image_data, name=result_filename)
        job.result_image.save(result_filename, result_file)
        
        # Update status
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save()
        
        print(f"✅ Face swap job {job_id} completed successfully")
        return True
        
    except FaceSwapJob.DoesNotExist:
        print(f"❌ Face swap job {job_id} not found")
        return False
    except Exception as e:
        print(f"❌ Face swap job {job_id} failed: {e}")
        try:
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
        except:
            pass
        return False