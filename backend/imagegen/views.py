from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .replicate_utils import generate_image_from_prompt, get_prediction_status
from .models import GeneratedImage
from .serializers import GeneratedImageSerializer

class GenerateImageView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        prompt = request.data.get("prompt")
        selfie = request.FILES.get("selfie")
        match_name = request.data.get("match_name")

        if not prompt or not selfie or not match_name:
            return Response({"error": "Prompt, selfie, and match_name are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Save selfie for tracking
        temp_image = GeneratedImage.objects.create(
            user=request.user if request.user.is_authenticated else None,
            prompt=prompt,
            match_name=match_name,
            selfie=selfie,
            output_url="",
        )

        result = generate_image_from_prompt(prompt)
        request.session[f"pending_image_{result['prediction_id']}"] = temp_image.id
        return Response(result)

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
