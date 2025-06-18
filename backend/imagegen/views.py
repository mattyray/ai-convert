from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import GeneratedImage
from .face_match import match_face
import tempfile
import base64
from django.core.files.base import ContentFile
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
import io
import time
import random
import requests
import json

# Map historical figures to their Cloudinary URLs
HISTORICAL_FIGURES = {
    "Princess Diana": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921365/princess_diana_ueb9ha.png",
    "Marilyn Monroe": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921365/marilyn_monroe_geys6v.png",
    "Pocahontas": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921365/Pocahontas_kp0obo.png",
    "Napoleon": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921365/napolean_ukozvo.png",
    "Marie Antoinette": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921363/Marie_Antoinette_fvjtgy.png",
    "Keith Haring": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921362/keith_k7b5xw.png",
    "Malcolm X": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921362/malcolm_x_a8sluo.png",
    "Jimi Hendrix": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921362/jimi_hendrix_u07bvu.png",
    "Joan of Arc": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921362/Joan_of_Arc_vvi28l.png",
    "Leonardo da Vinci": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921362/leonardo_davinci_lv7gy8.png",
    "Cleopatra": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921359/cleopatra_zcslcx.png",
    "Frida Kahlo": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921358/frida_khalo_wq6qyl.png",
    "JFK": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921358/jfk_rznzq0.png",
    "James Dean": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921358/james_dean_wvmc5c.png",
    "Coco Chanel": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921358/Coco_Chanel_mnx6s9.png",
    "Elvis Presley": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921841/elvis_heazqa.png",
    "Che Guevara": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921355/Che_Guevara_n8nmln.png",
    "Alexander the Great": "https://res.cloudinary.com/dddye9wli/image/upload/v1749921354/alexander_the_great_mcdwpy.png",
}

HUGGINGFACE_SPACE_URL = "https://mnraynor90-facefusionfastapi.hf.space"

def get_image_url(image_field):
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
                    # Fallback to absolute URL
                    from django.conf import settings
                    base_url = getattr(settings, 'BASE_URL', 'http://127.0.0.1:8002')
                    return f"{base_url}{image_url}"
            
            return image_url
        else:
            raise Exception("Invalid image field")
    except Exception as e:
        raise Exception(f"Failed to get image URL: {str(e)}")

def perform_face_swap_direct_http(source_url, target_url, max_retries=4):
    """
    Use direct HTTP POST like the working test-url endpoint
    """
    for attempt in range(max_retries):
        try:
            print(f"🔄 Direct HTTP face swap attempt {attempt + 1}/{max_retries}")
            print(f"  Source: {source_url[:80]}...")
            print(f"  Target: {target_url[:80]}...")
            
            # Use the same direct HTTP approach as test-url
            response = requests.post(
                f"{HUGGINGFACE_SPACE_URL}/run/predict",
                headers={
                    "Content-Type": "application/json",
                },
                json={
                    "data": [source_url, target_url]
                },
                timeout=120
            )
            
            print(f"📋 HTTP Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📋 Response data keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
                
                # Handle the response format
                if "data" in result and isinstance(result["data"], list) and len(result["data"]) >= 1:
                    image_data = result["data"][0]
                    
                    # Handle base64 image data
                    if isinstance(image_data, str) and image_data.startswith("data:image"):
                        # Extract base64 data
                        base64_data = image_data.split(",")[1]
                        image_bytes = base64.b64decode(base64_data)
                        print(f"✅ Got base64 image: {len(image_bytes)} bytes")
                        return image_bytes
                    
                    # Handle file path or other formats
                    elif isinstance(image_data, dict) and "path" in image_data:
                        # This would need additional handling for file paths
                        raise Exception("File path response not yet supported in direct HTTP mode")
                    
                    else:
                        raise Exception(f"Unexpected image data format: {type(image_data)}")
                else:
                    raise Exception(f"Invalid response format: {result}")
            
            else:
                error_msg = response.text
                print(f"❌ HTTP error {response.status_code}: {error_msg}")
                
                # Check for rate limiting
                if any(keyword in error_msg.lower() for keyword in [
                    'slow down', 'too many', 'rate limit', 'concurrent requests',
                    'quota exceeded', 'throttled', 'busy'
                ]):
                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter for rate limits
                        base_delay = 3 ** attempt  # 1s, 3s, 9s, 27s
                        jitter = random.uniform(0.7, 1.3)
                        delay = base_delay * jitter
                        
                        print(f"⏳ Rate limited. Waiting {delay:.1f}s before retry {attempt + 2}...")
                        time.sleep(delay)
                        continue
                    else:
                        raise Exception("Rate limited after all retries. Please try again in a few minutes.")
                else:
                    raise Exception(f"HTTP error {response.status_code}: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                delay = 2 + random.uniform(0, 2)
                print(f"⏳ Retrying in {delay:.1f}s...")
                time.sleep(delay)
                continue
            else:
                raise Exception(f"Face swap failed after {max_retries} attempts. Last error: {e}")
        
        except Exception as e:
            print(f"❌ Unexpected error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                delay = 2 + random.uniform(0, 2)
                print(f"⏳ Retrying in {delay:.1f}s...")
                time.sleep(delay)
                continue
            else:
                raise e
    
    raise Exception(f"Face swap failed after {max_retries} attempts")

class GenerateImageView(APIView):
    permission_classes = [permissions.AllowAny]

    def perform_face_swap_with_retry(self, source_mock, target_mock, match_name, max_retries=4):
        """
        Perform face swap using direct HTTP (like test-url endpoint)
        """
        # Get URLs from mock objects
        source_url = get_image_url(source_mock)
        target_url = get_image_url(target_mock)
        
        print(f"🔄 Starting face swap for {match_name}")
        print(f"  Source URL: {source_url}")
        print(f"  Target URL: {target_url}")
        
        # Use direct HTTP approach (same as working test-url)
        return perform_face_swap_direct_http(source_url, target_url, max_retries)

    def post(self, request):
        selfie = request.FILES.get("selfie")
        if not selfie:
            return Response({"error": "Selfie is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Read the file content once and store it
        selfie_content = selfie.read()
        
        # Save uploaded selfie to temporary file for face matching
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(selfie_content)
            tmp_path = tmp.name

        # Create a new file object for Django model (reset file pointer)
        selfie_for_model = InMemoryUploadedFile(
            file=io.BytesIO(selfie_content),
            field_name=selfie.field_name,
            name=selfie.name,
            content_type=selfie.content_type,
            size=len(selfie_content),
            charset=selfie.charset,
        )

        temp_image = None
        try:
            # Step 1: Match face with historical figures
            print("🔍 Starting face matching...")
            match_result = match_face(tmp_path)
            if "error" in match_result:
                return Response(match_result, status=status.HTTP_400_BAD_REQUEST)

            match_name = match_result["match_name"]
            match_score = match_result.get("score", 0)
            
            print(f"🎯 Face match found: {match_name} (score: {match_score:.3f})")

            # Check if we have a historical image for this match
            historical_image_url = HISTORICAL_FIGURES.get(match_name)
            if not historical_image_url:
                return Response({
                    "error": f"No historical image available for {match_name}. Available figures: {list(HISTORICAL_FIGURES.keys())}"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Step 2: Create database record with the fresh file object
            temp_image = GeneratedImage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                prompt=f"You as {match_name}",
                match_name=match_name,
                selfie=selfie_for_model,
                output_url="",
            )

            print(f"📝 Created GeneratedImage record: {temp_image.id}")

            # Step 3: Create mock image field objects for face swap
            class MockImageField:
                def __init__(self, url):
                    self.url = url

            source_mock = MockImageField(temp_image.selfie.url)  # User's selfie
            target_mock = MockImageField(historical_image_url)   # Historical figure

            print(f"🔄 Starting face swap: {temp_image.selfie.url} -> {historical_image_url}")

            # Step 4: Perform face swap with retry logic (NOW USING DIRECT HTTP)
            result_image_data = self.perform_face_swap_with_retry(
                source_mock, target_mock, match_name
            )

            print(f"✅ Face swap completed: {len(result_image_data)} bytes")

            # Step 5: Save the result
            temp_image.output_image.save(
                f"{temp_image.id}_fused_{match_name.replace(' ', '_')}.jpg", 
                ContentFile(result_image_data)
            )
            temp_image.save()

            print(f"💾 Saved result to: {temp_image.output_image.url}")

            return Response({
                "id": temp_image.id,
                "match_name": match_name,
                "match_score": round(match_score, 3),
                "message": f"Successfully transformed you into {match_name}!",
                "output_image_url": temp_image.output_image.url,
                "original_selfie_url": temp_image.selfie.url,
                "historical_figure_url": historical_image_url
            })

        except Exception as e:
            print(f"❌ Error in GenerateImageView: {str(e)}")
            # Clean up on error
            if temp_image:
                try:
                    temp_image.delete()
                except:
                    pass
            
            return Response({
                "error": f"Face processing failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass


class ImageStatusView(APIView):
    """Get status of a generated image"""
    def get(self, request, prediction_id):
        try:
            generated_image = GeneratedImage.objects.get(id=prediction_id)
            
            return Response({
                "id": generated_image.id,
                "status": "completed" if generated_image.output_image else "processing",
                "match_name": generated_image.match_name,
                "prompt": generated_image.prompt,
                "output_image_url": generated_image.output_image.url if generated_image.output_image else None,
                "created_at": generated_image.created_at
            })
        except GeneratedImage.DoesNotExist:
            return Response(
                {"error": "Generated image not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )


class UnlockImageView(APIView):
    """Reset generation counter for demo purposes"""
    def post(self, request):
        request.session["image_generation_count"] = 0
        return Response({"message": "Unlock granted. You can generate again."})


class ListGeneratedImagesView(APIView):
    """List all generated images for a user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        images = GeneratedImage.objects.filter(user=request.user).order_by('-created_at')
        
        results = []
        for img in images:
            results.append({
                "id": img.id,
                "match_name": img.match_name,
                "prompt": img.prompt,
                "output_image_url": img.output_image.url if img.output_image else None,
                "selfie_url": img.selfie.url,
                "created_at": img.created_at
            })
        
        return Response({"images": results})