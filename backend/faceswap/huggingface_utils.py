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
        Call your Hugging Face Space FastAPI to perform face swapping
        """
        try:
            # Prepare files for upload to FastAPI
            with open(source_image_path, 'rb') as source_file, \
                 open(target_image_path, 'rb') as target_file:
                
                files = {
                    'source_image': ('source.jpg', source_file, 'image/jpeg'),
                    'target_image': ('target.jpg', target_file, 'image/jpeg')
                }
                
                # Try multiple possible FastAPI endpoints
                endpoints_to_try = [
                    "/swap_faces",
                    "/faceswap", 
                    "/predict",
                    "/api/swap_faces",
                    "/api/faceswap"
                ]
                
                for endpoint in endpoints_to_try:
                    try:
                        response = requests.post(
                            f"{self.base_url}{endpoint}",
                            files=files,
                            timeout=300  # 5 minutes timeout
                        )
                        
                        if response.status_code == 200:
                            # Success! Process the response
                            break
                        elif response.status_code == 404:
                            # Try next endpoint
                            continue
                        else:
                            raise Exception(f"API call failed: {response.status_code} - {response.text}")
                    except requests.exceptions.RequestException as e:
                        if endpoint == endpoints_to_try[-1]:  # Last endpoint failed
                            raise e
                        continue
                else:
                    # All endpoints failed
                    raise Exception(f"All API endpoints failed. Tried: {endpoints_to_try}")
            
            # Reset file pointers for response processing
            source_file.seek(0)
            target_file.seek(0)
            
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