# faceswap/huggingface_utils.py - SOLUTION 1: Client.duplicate() approach

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

# 🔗 HuggingFace Space Configuration
HUGGINGFACE_SPACE_URL = getattr(settings, 'HUGGINGFACE_FACESWAP_URL', 
                               'https://mnraynor90-facefusionfastapi-private.hf.space')

# 🔑 HuggingFace Authentication Token (from environment)
HUGGINGFACE_API_TOKEN = getattr(settings, 'HUGGINGFACE_API_TOKEN', None)

class SingletonGradioClient:
    """
    SOLUTION 1: Use Client.duplicate() to create unlimited-usage private space
    This bypasses ALL rate limiting by creating your own copy of the space
    """
    _instance = None
    _client = None
    _duplicated_space_url = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SingletonGradioClient, cls).__new__(cls)
        return cls._instance
    
    def get_client(self):
        """Get duplicated space client - ELIMINATES RATE LIMITING COMPLETELY!"""
        if self._client is None:
            with self._lock:
                if self._client is None:
                    try:
                        print("🔌 Creating DUPLICATED space client...")
                        print(f"🏠 Original Space: {HUGGINGFACE_SPACE_URL}")
                        
                        if not HUGGINGFACE_API_TOKEN:
                            raise Exception("HUGGINGFACE_API_TOKEN required for space duplication!")
                        
                        print(f"🔑 Token: {HUGGINGFACE_API_TOKEN[:10]}... ✅")
                        
                        # 🌟 THE ULTIMATE FIX: Duplicate the space for unlimited usage!
                        # This creates a private copy that bypasses all rate limiting
                        print("🚀 Duplicating space for unlimited usage...")
                        
                        # Extract space name from URL
                        # https://mnraynor90-facefusionfastapi-private.hf.space → mnraynor90/facefusionfastapi-private
                        space_name = "mnraynor90/facefusionfastapi-private"
                        
                        print(f"📋 Duplicating space: {space_name}")
                        
                        self._client = Client.duplicate(
                            space_name,
                            hf_token=HUGGINGFACE_API_TOKEN,
                            private=True,  # Keep it private
                            hardware="t4-small"  # Match your T4 hardware
                        )
                        
                        print("✅ DUPLICATED space client created successfully!")
                        print("🚫 Rate limiting is now COMPLETELY ELIMINATED!")
                        print("💰 You own this space copy - unlimited requests!")
                        
                    except Exception as e:
                        print(f"❌ Failed to duplicate space: {e}")
                        print("💡 Falling back to direct connection...")
                        
                        # Fallback to direct connection with auth
                        self._client = Client(
                            HUGGINGFACE_SPACE_URL, 
                            hf_token=HUGGINGFACE_API_TOKEN
                        )
                        print("⚠️ Using direct connection - may still hit rate limits")
                        
        return self._client
    
    def reset_client(self):
        """Reset the client if it becomes invalid"""
        with self._lock:
            print("🔄 Resetting duplicated space client...")
            self._client = None

# Global singleton instance
gradio_singleton = SingletonGradioClient()

class FaceFusionClient:
    """
    Enhanced FaceFusion client using duplicated space (unlimited usage)
    """
    
    def __init__(self):
        self.base_url = HUGGINGFACE_SPACE_URL
        
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
    
    def swap_faces(self, source_image_field, target_image_field, max_retries=2):
        """
        Perform face swap using DUPLICATED SPACE - unlimited usage!
        """
        # Get URLs
        source_url = self.get_image_url(source_image_field)
        target_url = self.get_image_url(target_image_field)
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 DUPLICATED SPACE face swap attempt {attempt + 1}/{max_retries}")
                print(f"  Source: {source_url[:80]}...")
                print(f"  Target: {target_url[:80]}...")
                
                # Use the DUPLICATED space client (unlimited usage!)
                client = gradio_singleton.get_client()
                
                # Call the API on your private duplicated space
                result = client.predict(
                    source_url,
                    target_url,
                    api_name="/process_images"
                )
                
                print(f"📋 Result type: {type(result)}, length: {len(result) if result else 0}")
                
                if not result or len(result) < 2:
                    raise Exception(f"Invalid result format: {result}")
                
                result_image = result[0]
                status_message = result[1]
                
                print(f"📋 Status: {status_message}")
                
                # Handle different result types
                if hasattr(result_image, 'save'):  # PIL Image
                    print("✅ Got PIL Image, converting to bytes")
                    import io
                    img_buffer = io.BytesIO()
                    result_image.save(img_buffer, format='JPEG', quality=90)
                    return img_buffer.getvalue()
                    
                elif isinstance(result_image, str) and os.path.exists(result_image):  # File path
                    print(f"✅ Got file path: {result_image}")
                    with open(result_image, 'rb') as f:
                        return f.read()
                        
                elif isinstance(result_image, dict) and 'path' in result_image:  # Dict with path
                    file_path = result_image['path']
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            return f.read()
                            
                else:
                    raise Exception(f"Unexpected result format: {type(result_image)}")
                    
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                
                # With duplicated space, rate limiting should be impossible
                if 'slow down' in error_msg or 'too many' in error_msg or 'rate limit' in error_msg:
                    print("🚨 UNEXPECTED: Still getting rate limited with duplicated space!")
                    print("💡 This suggests duplication failed - check logs above")
                    
                    if attempt < max_retries - 1:
                        gradio_singleton.reset_client()
                        delay = 5 + random.uniform(0, 3)
                        print(f"⏳ Resetting and waiting {delay:.1f}s...")
                        time.sleep(delay)
                        continue
                    else:
                        raise Exception("Rate limited even with duplicated space - check HUGGINGFACE_API_TOKEN!")
                
                # For other errors, shorter delay
                elif attempt < max_retries - 1:
                    delay = 3 + random.uniform(0, 2)
                    print(f"⏳ Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                else:
                    break
        
        # All attempts failed
        raise Exception(f"Face swap failed after {max_retries} attempts. Last error: {last_error}")

def process_face_swap(job_id):
    """
    Process a face swap job using DUPLICATED SPACE (unlimited usage)
    """
    from .models import FaceSwapJob
    from django.utils import timezone
    
    try:
        job = FaceSwapJob.objects.get(id=job_id)
        job.status = 'processing'
        job.save()
        
        print(f"🚀 Processing face swap job {job_id} with DUPLICATED SPACE")
        
        # Initialize client
        client = FaceFusionClient()
        
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
        
        print(f"✅ Face swap job {job_id} completed successfully with DUPLICATED SPACE")
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