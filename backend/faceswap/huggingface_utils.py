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
        
    def upload_image_to_temp_url(self, image_path):
        """Upload image to a temporary hosting service to get a URL"""
        try:
            # Use a simple image hosting service like imgbb or similar
            # For now, we'll convert to base64 data URL
            with open(image_path, 'rb') as f:
                image_data = f.read()
                encoded = base64.b64encode(image_data).decode('utf-8')
                # Detect image format
                if image_path.lower().endswith('.png'):
                    data_url = f"data:image/png;base64,{encoded}"
                else:
                    data_url = f"data:image/jpeg;base64,{encoded}"
                return data_url
        except Exception as e:
            raise Exception(f"Failed to create data URL: {str(e)}")
        
    def swap_faces(self, source_image_path, target_image_path):
        """
        Call your Hugging Face Space Gradio API to perform face swapping
        """
        try:
            # Method 1: Try using gradio_client
            try:
                client = Client(self.base_url)
                
                # Your Gradio app expects URLs, so we need to convert files to URLs
                source_url = self.upload_image_to_temp_url(source_image_path)
                target_url = self.upload_image_to_temp_url(target_image_path)
                
                # Call the Gradio function (assuming it's the first/default function)
                result = client.predict(
                    source_url,  # source_input
                    target_url,  # target_input
                    api_name="/predict"
                )
                
                # Result should be [image, status_message]
                if result and len(result) >= 2:
                    result_image = result[0]  # The image result
                    status_message = result[1]  # Status message
                    
                    if result_image:
                        # Convert PIL Image to bytes
                        from PIL import Image
                        import io
                        
                        if isinstance(result_image, str):
                            # If it's a file path, read it
                            with open(result_image, 'rb') as f:
                                return f.read()
                        elif hasattr(result_image, 'save'):
                            # If it's a PIL Image
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
                source_url = self.upload_image_to_temp_url(source_image_path)
                target_url = self.upload_image_to_temp_url(target_image_path)
                
                # Try the Gradio API endpoint
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
                            if result_image.startswith('data:image'):
                                # Base64 data URL
                                header, encoded = result_image.split(',', 1)
                                return base64.b64decode(encoded)
                            else:
                                # File path - try to download
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
        
        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as source_temp, \
             tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as target_temp:
            
            # Copy uploaded images to temp files
            source_temp.write(job.source_image.read())
            target_temp.write(job.target_image.read())
            source_temp.flush()
            target_temp.flush()
            
            # Initialize FaceFusion client
            client = FaceFusionClient()
            
            # Perform face swap
            result_image_data = client.swap_faces(source_temp.name, target_temp.name)
            
            # Save result image
            result_filename = f"faceswap_result_{job.id}_{int(time.time())}.jpg"
            result_file = ContentFile(result_image_data, name=result_filename)
            job.result_image.save(result_filename, result_file)
            
            # Update job status
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.save()
            
        # Clean up temp files
        os.unlink(source_temp.name)
        os.unlink(target_temp.name)
        
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