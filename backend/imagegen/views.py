from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .replicate_utils import generate_image_from_prompt, get_prediction_status
from .models import GeneratedImage
from .serializers import GeneratedImageSerializer
from .face_match import match_face
import tempfile

class GenerateImageView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        prompt_base = request.data.get("prompt", "A cinematic 4K portrait of")
        selfie = request.FILES.get("selfie")

        if not selfie:
            return Response({"error": "Selfie is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Enforce usage limit if anonymous
        if not request.user.is_authenticated:
            count = request.session.get("image_generation_count", 0)
            if count >= 1:
                return Response({
                    "error": "You’ve used your free generation. Please log in or watch an ad to unlock more."
                }, status=status.HTTP_403_FORBIDDEN)

        # Save selfie temporarily for face matching
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            for chunk in selfie.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        match_result = match_face(tmp_path)
        if "error" in match_result:
            return Response(match_result, status=status.HTTP_400_BAD_REQUEST)

        match_name = match_result["match_name"]
        prompt = f"{prompt_base} {match_name}, highly detailed, beautiful lighting"

        # Save permanent selfie and entry
        temp_image = GeneratedImage.objects.create(
            user=request.user if request.user.is_authenticated else None,
            prompt=prompt,
            match_name=match_name,
            selfie=selfie,
            output_url="",
        )

        result = generate_image_from_prompt(prompt)
        request.session[f"pending_image_{result['prediction_id']}"] = temp_image.id

        if not request.user.is_authenticated:
            request.session["image_generation_count"] = count + 1

        return Response({
            **result,
            "match_name": match_name
        })


class ImageStatusView(APIView):
    def get(self, request, prediction_id):
        result = get_prediction_status(prediction_id)

        if result.get("output"):
            gen_id = request.session.get(f"pending_image_{prediction_id}")
            if gen_id:
                try:
                    image = GeneratedImage.objects.get(id=gen_id)
                    image.output_url = result["output"][0]  # assuming first image
                    image.save()
                    del request.session[f"pending_image_{prediction_id}"]
                except GeneratedImage.DoesNotExist:
                    pass

        return Response(result)
