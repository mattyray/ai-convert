import requests
import time
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import tempfile
import os
import base64
from gradio_client import Client

# Your specific Hugging Face Space URL
HUGGINGFACE_SPACE_URL = getattr(settings, 'HUGGINGFACE_FACESWAP_URL', 
                               'https://mnraynor90-facefusionfastapi.hf.space')

class FaceFusionClient:
    def __init__(self):
        self.base_url = HUGGINGFACE_SPACE_URL
        
    def get_image_url(self, image_field):
        """Convert Django ImageField to accessible URL"""
        try:
            if hasattr(image_field, 'url'):
                image_url = image_field.url
                # If it's a relative URL, make it absolute
                if image_url.startswith('/'):
                    # For local development - you'd want your actual domain in production
                    base_url = getattr(settings, 'BASE_URL', 'http://127.0.0.1:8002')
                    image_url = f"{base_url}{image_url}"
                return image_url
            else:
                raise Exception("Invalid image field")
        except Exception as e:
            raise Exception(f"Failed to get image URL: {str(e)}")
        
    def swap_faces(self, source_image_field, target_image_field):
        """
        Call your Hugging Face Space Gradio API to perform face swapping
        """
        try:
            # Get URLs for the images (works with Cloudinary or local URLs)
            source_url = self.get_image_url(source_image_field)
            target_url = self.get_image_url(target_image_field)
            
            print(f"Source URL: {source_url}")
            print(f"Target URL: {target_url}")
            
            # Method 1: Try using gradio_client
            try:
                client = Client(self.base_url)
                
                # Call the Gradio function with URLs
                result = client.predict(
                    source_url,  # source_input
                    target_url,  # target_input
                    api_name="/predict"
                )
                
                print(f"Gradio result: {result}")
                
                # Result should be [image, status_message]
                if result and len(result) >= 2:
                    result_image = result[0]  # The image result
                    status_message = result[1]  # Status message
                    
                    print(f"Status message: {status_message}")
                    
                    if result_image:
                        # Handle different result types
                        if isinstance(result_image, str):
                            if result_image.startswith('http'):
                                # It's a URL - download it
                                img_response = requests.get(result_image)
                                if img_response.status_code == 200:
                                    return img_response.content
                                else:
                                    raise Exception(f"Failed to download result image: {img_response.status_code}")
                            elif os.path.exists(result_image):
                                # It's a local file path
                                with open(result_image, 'rb') as f:
                                    return f.read()
                            else:
                                raise Exception(f"Invalid result image path: {result_image}")
                        elif hasattr(result_image, 'save'):
                            # If it's a PIL Image
                            from PIL import Image
                            import io
                            img_buffer = io.BytesIO()
                            result_image.save(img_buffer, format='JPEG')
                            return img_buffer.getvalue()
                        else:
                            raise Exception(f"Unexpected image result type: {type(result_image)}")
                    else:
                        raise Exception(f"No image result. Status: {status_message}")
                else:
                    raise Exception(f"Unexpected result format: {result}")
                    
            except Exception as gradio_error:
                print(f"Gradio client failed: {gradio_error}")
                
                # Method 2: Try direct HTTP calls to Gradio API
                payload = {
                    "data": [source_url, target_url]
                }
                
                response = requests.post(
                    f"{self.base_url}/run/predict",
                    json=payload,
                    timeout=300
                )
                
                if response.status_code == 200:
                    result_data = response.json()
                    
                    if 'data' in result_data and result_data['data']:
                        # First element should be the image
                        result_image = result_data['data'][0]
                        
                        if isinstance(result_image, str):
                            if result_image.startswith('http'):
                                # Download the result
                                file_response = requests.get(result_image)
                                if file_response.status_code == 200:
                                    return file_response.content
                                else:
                                    raise Exception(f"Failed to download result: {file_response.status_code}")
                            elif result_image.startswith('data:image'):
                                # Base64 data URL
                                header, encoded = result_image.split(',', 1)
                                return base64.b64decode(encoded)
                            else:
                                # Try as file path
                                file_response = requests.get(f"{self.base_url}/file={result_image}")
                                if file_response.status_code == 200:
                                    return file_response.content
                                else:
                                    raise Exception(f"Failed to download result: {file_response.status_code}")
                        else:
                            raise Exception(f"Unexpected result format: {type(result_image)}")
                    else:
                        raise Exception(f"No data in API response: {result_data}")
                else:
                    raise Exception(f"HTTP request failed: {response.status_code} - {response.text}")
                    
        except requests.exceptions.Timeout:
            raise Exception("Request timed out - face swapping took too long")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise Exception(f"Face swapping failed: {str(e)}")

def process_face_swap(job_id):
    """
    Process a face swap job using Hugging Face Space
    """
    from .models import FaceSwapJob
    from django.utils import timezone
    
    try:
        job = FaceSwapJob.objects.get(id=job_id)
        job.status = 'processing'
        job.save()
        
        # Initialize FaceFusion client
        client = FaceFusionClient()
        
        # Perform face swap using the ImageField objects directly
        result_image_data = client.swap_faces(job.source_image, job.target_image)
        
        # Save result image
        result_filename = f"faceswap_result_{job.id}_{int(time.time())}.jpg"
        result_file = ContentFile(result_image_data, name=result_filename)
        job.result_image.save(result_filename, result_file)
        
        # Update job status
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save()
        
        return True
        
    except FaceSwapJob.DoesNotExist:
        print(f"FaceSwap job {job_id} not found")
        return False
    except Exception as e:
        # Update job with error
        try:
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
        except:
            pass
        print(f"FaceSwap job {job_id} failed: {str(e)}")
        return False