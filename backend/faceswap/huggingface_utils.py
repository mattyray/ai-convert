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
            
            # Create a temporary directory for downloads
            download_dir = tempfile.mkdtemp()
            print(f"Download directory: {download_dir}")
            
            # Use the correct endpoint with download_files enabled
            client = Client(
                "mnraynor90/facefusionfastapi",
                download_files=True,  # Enable automatic file downloads
                download_dir=download_dir  # Specify download directory
            )
            
            # Call the process_images function
            result = client.predict(
                source_url=source_url,
                target_url=target_url,
                api_name="/process_images"
            )
            
            print(f"Gradio result: {result}")
            
            # Result is tuple of 2 elements: [image_path_or_dict, status_message]
            if result and len(result) >= 2:
                result_image = result[0]  # Could be path string or dict
                status_message = result[1]  # Status message
                
                print(f"Status message: {status_message}")
                print(f"Image result type: {type(result_image)}")
                print(f"Image result content: {result_image}")
                
                # Handle both string path and dict formats
                if isinstance(result_image, str):
                    # It should now be a local file path due to download_files=True
                    print(f"Local image path: {result_image}")
                    
                    if os.path.exists(result_image):
                        print(f"File exists! Size: {os.path.getsize(result_image)} bytes")
                        with open(result_image, 'rb') as f:
                            image_data = f.read()
                            print(f"Successfully read {len(image_data)} bytes from local file")
                            
                            # Clean up the download directory
                            try:
                                import shutil
                                shutil.rmtree(download_dir)
                                print(f"Cleaned up download directory: {download_dir}")
                            except Exception as cleanup_error:
                                print(f"Failed to cleanup download dir: {cleanup_error}")
                            
                            return image_data
                    else:
                        # File doesn't exist locally, maybe it's still a remote path
                        print(f"Local file doesn't exist, trying remote download fallback")
                        raise Exception(f"Local file not found and remote download failed: {result_image}")
                
                elif isinstance(result_image, dict):
                    # It's a dict with url/path - check if it has a local path first
                    local_path = result_image.get('path')
                    image_url = result_image.get('url')
                    
                    print(f"Dict result - path: {local_path}, url: {image_url}")
                    
                    if local_path and os.path.exists(local_path):
                        with open(local_path, 'rb') as f:
                            image_data = f.read()
                            # Clean up
                            try:
                                import shutil
                                shutil.rmtree(download_dir)
                            except:
                                pass
                            return image_data
                    
                    elif image_url:
                        # Try downloading from URL as fallback
                        print(f"Downloading from URL fallback: {image_url}")
                        img_response = requests.get(image_url)
                        if img_response.status_code == 200:
                            # Clean up
                            try:
                                import shutil
                                shutil.rmtree(download_dir)
                            except:
                                pass
                            return img_response.content
                        else:
                            raise Exception(f"Failed to download from URL: {img_response.status_code}")
                    
                    else:
                        raise Exception(f"No valid path or URL in image dict: {result_image}")
                
                else:
                    raise Exception(f"Unexpected image result type: {type(result_image)}")
            
            else:
                raise Exception(f"Unexpected result format: {result}")
                    
        except Exception as e:
            print(f"Face swap error: {str(e)}")
            # Clean up download directory on error
            try:
                if 'download_dir' in locals():
                    import shutil
                    shutil.rmtree(download_dir)
            except:
                pass
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