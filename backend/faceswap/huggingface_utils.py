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
            
            # Use the correct endpoint from your Space documentation
            client = Client("mnraynor90/facefusionfastapi")
            
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
                
                # Handle both string path and dict formats
                if isinstance(result_image, str):
                    # It's a file path - download it from Gradio
                    print(f"Image path: {result_image}")
                    
                    # Try multiple URL formats for Gradio file access
                    possible_urls = [
                        # Standard Gradio file endpoint
                        f"{self.base_url}/file{result_image}",
                        # Alternative format without =
                        f"{self.base_url}/file/{result_image.lstrip('/')}",
                        # With gradio prefix
                        f"{self.base_url}/gradio_api/file{result_image}",
                        # Direct file access
                        f"{self.base_url}{result_image}",
                    ]
                    
                    # Try each URL format
                    for download_url in possible_urls:
                        print(f"Trying download from: {download_url}")
                        
                        try:
                            img_response = requests.get(download_url, timeout=30)
                            print(f"Response status: {img_response.status_code}")
                            
                            if img_response.status_code == 200:
                                content_length = len(img_response.content)
                                print(f"Successfully downloaded {content_length} bytes")
                                
                                # Verify it's actually image data
                                if content_length > 1000:  # Should be at least 1KB for a real image
                                    return img_response.content
                                else:
                                    print(f"Content too small ({content_length} bytes), trying next URL")
                                    continue
                            else:
                                print(f"Failed with status {img_response.status_code}: {img_response.text[:100]}")
                                
                        except Exception as url_error:
                            print(f"Error with URL {download_url}: {str(url_error)}")
                            continue
                    
                    # If all URLs failed, raise an error
                    raise Exception(f"Could not download image from any URL. Last path: {result_image}")
                
                elif isinstance(result_image, dict):
                    # It's a dict with url/path - handle as before
                    image_url = result_image.get('url')
                    image_path = result_image.get('path')
                    
                    if image_url:
                        print(f"Downloading from URL: {image_url}")
                        img_response = requests.get(image_url)
                        if img_response.status_code == 200:
                            return img_response.content
                        else:
                            raise Exception(f"Failed to download from URL: {img_response.status_code}")
                    
                    elif image_path:
                        # Try the same multiple URL approach for dict paths
                        possible_urls = [
                            f"{self.base_url}/file{image_path}",
                            f"{self.base_url}/file/{image_path.lstrip('/')}",
                            f"{self.base_url}/gradio_api/file{image_path}",
                        ]
                        
                        for download_url in possible_urls:
                            try:
                                img_response = requests.get(download_url)
                                if img_response.status_code == 200:
                                    return img_response.content
                            except:
                                continue
                        
                        raise Exception(f"Failed to download from path: {image_path}")
                    
                    else:
                        raise Exception(f"No valid URL or path in image dict: {result_image}")
                
                else:
                    raise Exception(f"Unexpected image result type: {type(result_image)}")
            
            else:
                raise Exception(f"Unexpected result format: {result}")
                    
        except Exception as e:
            print(f"Face swap error: {str(e)}")
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