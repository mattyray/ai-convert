# imagegen/views/generation_views.py - Core face generation functionality

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ..models import GeneratedImage, UsageSession
from ..face_match import match_face
from faceswap.huggingface_utils import FaceFusionClient
import tempfile
from django.core.files.base import ContentFile
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
import io
from django.core.cache import cache
from ..utils import compress_image
from ..data.historical_figures import HISTORICAL_FIGURES, get_random_figure


# 🔥 Memory management settings
MAX_CONCURRENT_JOBS = 2  # Limit simultaneous face swaps


class GenerateImageView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Check server capacity
        active_jobs = cache.get('active_face_swap_jobs', 0)
        if active_jobs >= MAX_CONCURRENT_JOBS:
            return Response({"error": "Server busy. Try again in 30 seconds.", "retry_after": 30}, status=503)

        selfie = request.FILES.get("selfie")
        if not selfie:
            return Response({"error": "Selfie is required"}, status=400)

        # Get usage session from middleware
        usage_session = getattr(request, 'usage_session', None)
        
        # Compress image
        compressed_selfie = compress_image(selfie)
        selfie_content = compressed_selfie.read()
        selfie_for_model = InMemoryUploadedFile(
            file=io.BytesIO(selfie_content),
            field_name='selfie',
            name=f"compressed_{selfie.name}",
            content_type='image/jpeg',
            size=len(selfie_content),
            charset=None,
        )

        # Save to temp file for face matching
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(selfie_content)
            tmp_path = tmp.name

        temp_image = None
        try:
            # Increment job counter
            cache.set('active_face_swap_jobs', active_jobs + 1, timeout=300)
            
            # Face matching
            match_result = match_face(tmp_path)
            if "error" in match_result:
                return Response(match_result, status=status.HTTP_400_BAD_REQUEST)

            match_name = match_result["match_name"]
            match_score = match_result.get("score", 0)
            
            # Get historical image
            historical_image_url = HISTORICAL_FIGURES.get(match_name)
            if not historical_image_url:
                return Response({"error": f"No historical image available for {match_name}"}, status=400)

            # Create database record
            temp_image = GeneratedImage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                prompt=f"You as {match_name}",
                match_name=match_name,
                selfie=selfie_for_model,
                output_url="",
            )

            # Face swap
            class MockImageField:
                def __init__(self, url):
                    self.url = url

            source_mock = MockImageField(temp_image.selfie.url)
            target_mock = MockImageField(historical_image_url)

            client = FaceFusionClient()
            result_image_data = client.swap_faces(source_mock, target_mock)

            # Save result
            temp_image.output_image.save(
                f"{temp_image.id}_fused_{match_name.replace(' ', '_')}.jpg", 
                ContentFile(result_image_data)
            )
            temp_image.save()

            # Update usage for anonymous users
            if usage_session and not request.user.is_authenticated:
                usage_session.use_match()

            return Response({
                "id": temp_image.id,
                "match_name": match_name,
                "match_score": round(match_score, 3),
                "message": f"Successfully transformed you into {match_name}!",
                "output_image_url": temp_image.output_image.url,
                "original_selfie_url": temp_image.selfie.url,
                "historical_figure_url": historical_image_url,
                "usage": self.get_usage_data(request, usage_session)
            })

        except Exception as e:
            if temp_image:
                try:
                    temp_image.delete()
                except:
                    pass
            return Response({"error": f"Face processing failed: {str(e)}"}, status=500)
        
        finally:
            current_jobs = cache.get('active_face_swap_jobs', 1)
            cache.set('active_face_swap_jobs', max(0, current_jobs - 1), timeout=300)
            try:
                os.unlink(tmp_path)
            except:
                pass

    def get_usage_data(self, request, usage_session):
        if request.user.is_authenticated:
            return {"unlimited": True}
        elif usage_session:
            return {
                "matches_used": usage_session.matches_used,
                "matches_limit": usage_session.MAX_MATCHES,
                "randomizes_used": usage_session.randomizes_used,
                "randomizes_limit": usage_session.MAX_RANDOMIZES,
                "can_match": usage_session.can_match,
                "can_randomize": usage_session.can_randomize,
                "is_limited": usage_session.is_limited,
            }
        return None


class RandomizeImageView(APIView):
    """Randomize with random historical figure"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Check server capacity
        active_jobs = cache.get('active_face_swap_jobs', 0)
        if active_jobs >= MAX_CONCURRENT_JOBS:
            return Response({"error": "Server busy. Try again in 30 seconds.", "retry_after": 30}, status=503)

        selfie = request.FILES.get("selfie")
        if not selfie:
            return Response({"error": "Selfie is required"}, status=400)

        # Get usage session from middleware
        usage_session = getattr(request, 'usage_session', None)
        
        # Pick random figure using the new helper function
        random_figure, historical_image_url = get_random_figure()
        
        # Compress image
        compressed_selfie = compress_image(selfie)
        selfie_content = compressed_selfie.read()
        selfie_for_model = InMemoryUploadedFile(
            file=io.BytesIO(selfie_content),
            field_name='selfie',
            name=f"compressed_{selfie.name}",
            content_type='image/jpeg',
            size=len(selfie_content),
            charset=None,
        )

        temp_image = None
        try:
            # Increment job counter
            cache.set('active_face_swap_jobs', active_jobs + 1, timeout=300)

            # Create database record
            temp_image = GeneratedImage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                prompt=f"You as {random_figure} (randomized)",
                match_name=random_figure,
                selfie=selfie_for_model,
                output_url="",
            )

            # Face swap
            class MockImageField:
                def __init__(self, url):
                    self.url = url

            source_mock = MockImageField(temp_image.selfie.url)
            target_mock = MockImageField(historical_image_url)

            client = FaceFusionClient()
            result_image_data = client.swap_faces(source_mock, target_mock)

            # Save result
            temp_image.output_image.save(
                f"{temp_image.id}_randomized_{random_figure.replace(' ', '_')}.jpg", 
                ContentFile(result_image_data)
            )
            temp_image.save()

            # Update usage for anonymous users
            if usage_session and not request.user.is_authenticated:
                usage_session.use_randomize()

            return Response({
                "id": temp_image.id,
                "match_name": random_figure,
                "match_score": 1.0,
                "message": f"You've been randomly transformed into {random_figure}!",
                "output_image_url": temp_image.output_image.url,
                "original_selfie_url": temp_image.selfie.url,
                "historical_figure_url": historical_image_url,
                "is_randomized": True,
                "usage": self.get_usage_data(request, usage_session)
            })

        except Exception as e:
            if temp_image:
                try:
                    temp_image.delete()
                except:
                    pass
            return Response({"error": f"Randomized face processing failed: {str(e)}"}, status=500)
        
        finally:
            current_jobs = cache.get('active_face_swap_jobs', 1)
            cache.set('active_face_swap_jobs', max(0, current_jobs - 1), timeout=300)

    def get_usage_data(self, request, usage_session):
        if request.user.is_authenticated:
            return {"unlimited": True}
        elif usage_session:
            return {
                "matches_used": usage_session.matches_used,
                "matches_limit": usage_session.MAX_MATCHES,
                "randomizes_used": usage_session.randomizes_used,
                "randomizes_limit": usage_session.MAX_RANDOMIZES,
                "can_match": usage_session.can_match,
                "can_randomize": usage_session.can_randomize,
                "is_limited": usage_session.is_limited,
            }
        return None