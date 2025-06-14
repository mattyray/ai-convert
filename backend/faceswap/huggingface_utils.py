import requests
import time
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import tempfile
import os
import base64

# Your specific Hugging Face Space URL
HUGGINGFACE_SPACE_URL = getattr(settings, 'HUGGINGFACE_FACESWAP_URL', 
                               'https://mnraynor90-facefusionfastapi.hf.space')

class FaceFusionClient:
    def __init__(self):
        self.base_url = HUGGINGFACE_SPACE_URL
        
    def swap_faces(self, source_image_path, target_image_path):
        """
        Call your Hugging Face Space Gradio API to perform face swapping
        """
        try:
            # Read and encode images as base64
            with open(source_image_path, 'rb') as source_file:
                source_data = source_file.read()
                source_b64 = base64.b64encode(source_data).decode('utf-8')
                source_url = f"data:image/jpeg;base64,{source_b64}"
            
            with open(target_image_path, 'rb') as target_file:
                target_data = target_file.read()
                target_b64 = base64.b64encode(target_data).decode('utf-8')
                target_url = f"data:image/jpeg;base64,{target_b64}"
            
            # Prepare payload for Gradio API
            payload = {
                "data": [source_url, target_url]
            }
            
            # Call Gradio API endpoint
            response = requests.post(
                f"{self.base_url}/run/predict",
                json=payload,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                result_data = response.json()
                
                # Gradio returns data in 'data' field
                if 'data' in result_data and result_data['data']:
                    # The first item should be the result image (base64 encoded)
                    result_image_data = result_data['data'][0]
                    
                    # Handle different response formats
                    if isinstance(result_image_data, str):
                        if result_image_data.startswith('data:image'):
                            # Remove data URL prefix and decode base64
                            header, encoded = result_image_data.split(',', 1)
                            image_bytes = base64.b64decode(encoded)
                            return image_bytes
                        else:
                            # Might be a file path - try to fetch it
                            file_response = requests.get(f"{self.base_url}/file={result_image_data}")
                            if file_response.status_code == 200:
                                return file_response.content
                            else:
                                raise Exception(f"Failed to download result file: {file_response.status_code}")
                    else:
                        raise Exception(f"Unexpected result format: {type(result_image_data)}")
                else:
                    raise Exception(f"No result image in API response: {result_data}")
            else:
                raise Exception(f"API call failed: {response.status_code} - {response.text}")
                    
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