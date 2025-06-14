from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import GeneratedImage
from .face_match import match_face
from faceswap.huggingface_utils import FaceFusionClient  # Import your working face swap client
import tempfile
import base64
from django.core.files.base import ContentFile
import os

# Map historical figures to their image URLs
HISTORICAL_FIGURES = {
    "Napoleon": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Jacques-Louis_David_-_The_Emperor_Napoleon_in_His_Study_at_the_Tuileries_-_Google_Art_Project.jpg/512px-Jacques-Louis_David_-_The_Emperor_Napoleon_in_His_Study_at_the_Tuileries_-_Google_Art_Project.jpg",
    "Albert Einstein": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Einstein_1921_by_F_Schmutzer_-_restoration.jpg/512px-Einstein_1921_by_F_Schmutzer_-_restoration.jpg",
    "Cleopatra": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Kleopatra-VII.-Altes-Museum-Berlin1.jpg/512px-Kleopatra-VII.-Altes-Museum-Berlin1.jpg",
    "Leonardo da Vinci": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Leonardo_self.jpg/512px-Leonardo_self.jpg",
    "Joan of Arc": "https://res.cloudinary.com/dddye9wli/image/upload/v1749857225/elvisnotsinging_twnnta.png",
    # Add more historical figures as needed
}

class GenerateImageView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        selfie = request.FILES.get("selfie")
        if not selfie:
            return Response({"error": "Selfie is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Save uploaded selfie to temporary file for face matching
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            for chunk in selfie.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            # Step 1: Match face with historical figures
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

            # Step 2: Create database record
            temp_image = GeneratedImage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                prompt=f"You as {match_name}",
                match_name=match_name,
                selfie=selfie,
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

            # Step 4: Perform face swap using your working client
            fusion_client = FaceFusionClient()
            result_image_data = fusion_client.swap_faces(source_mock, target_mock)

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