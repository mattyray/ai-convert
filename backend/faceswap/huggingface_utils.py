import requests
import time
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import tempfile
import os
import base64
from gradio_client import Client
import json

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
            
            # Call the process_images function - this is the main one that works
            result = client.predict(
                source_url=source_url,
                target_url=target_url,
                api_name="/process_images"  # Use the correct endpoint name
            )
            
            print(f"RAW Gradio result: {result}")
            print(f"Result type: {type(result)}")
            print(f"Result length: {len(result) if hasattr(result, '__len__') else 'No length'}")
            
            # Result is tuple of 2 elements: [image_dict, status_message]
            if result and len(result) >= 2:
                result_image_dict = result[0]  # Image dict with path, url, etc.
                status_message = result[1]     # Status message
                
                print(f"Status message: {status_message}")
                print(f"Image dict type: {type(result_image_dict)}")
                print(f"Image dict content: {result_image_dict}")
                
                # Let's debug what's actually in the image dict
                if result_image_dict is not None:
                    if isinstance(result_image_dict, dict):
                        print(f"Image dict keys: {list(result_image_dict.keys())}")
                        for key, value in result_image_dict.items():
                            print(f"  {key}: {value} (type: {type(value)})")
                        
                        # Try all possible ways to get the image
                        image_url = result_image_dict.get('url')
                        image_path = result_image_dict.get('path')
                        
                        print(f"Extracted URL: {image_url}")
                        print(f"Extracted Path: {image_path}")
                        
                        if image_url:
                            print(f"Attempting to download from URL: {image_url}")
                            # Handle both absolute and relative URLs
                            if not image_url.startswith('http'):
                                # It might be a relative URL, make it absolute
                                image_url = f"{self.base_url}/file={image_url}"
                                print(f"Modified URL: {image_url}")
                            
                            img_response = requests.get(image_url)
                            print(f"Download response status: {img_response.status_code}")
                            print(f"Download response headers: {dict(img_response.headers)}")
                            
                            if img_response.status_code == 200:
                                print(f"Successfully downloaded {len(img_response.content)} bytes")
                                return img_response.content
                            else:
                                print(f"Failed to download. Response: {img_response.text[:200]}")
                        
                        elif image_path:
                            print(f"Attempting to read from path: {image_path}")
                            if os.path.exists(image_path):
                                with open(image_path, 'rb') as f:
                                    content = f.read()
                                    print(f"Successfully read {len(content)} bytes from file")
                                    return content
                            else:
                                print(f"Path does not exist: {image_path}")
                        
                        # If neither URL nor path worked, let's try to see if there's image data directly
                        for key in ['data', 'content', 'image', 'result']:
                            if key in result_image_dict:
                                print(f"Found potential image data in key '{key}': {type(result_image_dict[key])}")
                        
                        raise Exception(f"No valid image URL or path found. Dict contents: {result_image_dict}")
                    
                    else:
                        print(f"Image result is not a dict, it's: {type(result_image_dict)}")
                        print(f"Image result value: {result_image_dict}")
                        
                        # Maybe it's a direct image path or URL?
                        if isinstance(result_image_dict, str):
                            if result_image_dict.startswith('http'):
                                img_response = requests.get(result_image_dict)
                                if img_response.status_code == 200:
                                    return img_response.content
                            elif os.path.exists(result_image_dict):
                                with open(result_image_dict, 'rb') as f:
                                    return f.read()
                        
                        raise Exception(f"Unexpected image result type: {type(result_image_dict)}, value: {result_image_dict}")
                
                else:
                    print("Image dict is None!")
                    raise Exception(f"No image result (None). Status: {status_message}")
            
            else:
                raise Exception(f"Unexpected result format - length: {len(result) if hasattr(result, '__len__') else 'No length'}, content: {result}")
                    
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
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