from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .hf_utils import facefusion_via_hf
from .models import GeneratedImage
from .face_match import match_face
import tempfile
import base64
from django.core.files.base import ContentFile

NAPOLEON_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Jacques-Louis_David_-_The_Emperor_Napoleon_in_His_Study_at_the_Tuileries_-_Google_Art_Project.jpg/512px-Jacques-Louis_David_-_The_Emperor_Napoleon_in_His_Study_at_the_Tuileries_-_Google_Art_Project.jpg"

class GenerateImageView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        selfie = request.FILES.get("selfie")
        if not selfie:
            return Response({"error": "Selfie is required"}, status=status.HTTP_400_BAD_REQUEST)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            for chunk in selfie.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        match_result = match_face(tmp_path)
        if "error" in match_result:
            return Response(match_result, status=status.HTTP_400_BAD_REQUEST)

        match_name = match_result["match_name"]

        temp_image = GeneratedImage.objects.create(
            user=request.user if request.user.is_authenticated else None,
            prompt=f"You as {match_name}",
            match_name=match_name,
            selfie=selfie,
            output_url="",
        )

        selfie_url = temp_image.selfie.url
        result = facefusion_via_hf(selfie_url, NAPOLEON_IMAGE_URL)

        if "error" in result:
            temp_image.delete()
            return Response(result, status=status.HTTP_502_BAD_GATEWAY)

        img_data = base64.b64decode(result["base64"].split(",", 1)[-1])
        temp_image.output_image.save(f"{temp_image.id}_fused.jpg", ContentFile(img_data))
        temp_image.save()

        return Response({
            "match_name": match_name,
            "message": "Face fusion completed successfully.",
            "output_image_url": temp_image.output_image.url
        })


class ImageStatusView(APIView):
    def get(self, request, prediction_id):
        return Response({"error": "Not supported for Hugging Face flow"}, status=status.HTTP_400_BAD_REQUEST)


class UnlockImageView(APIView):
    def post(self, request):
        request.session["image_generation_count"] = 0
        return Response({"message": "Unlock granted. You can generate again."})
