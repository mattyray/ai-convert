from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .replicate_utils import generate_image_from_prompt, get_prediction_status

class GenerateImageView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt")
        if not prompt:
            return Response({"error": "Prompt is required."}, status=status.HTTP_400_BAD_REQUEST)
        result = generate_image_from_prompt(prompt)
        return Response(result)

class ImageStatusView(APIView):
    def get(self, request, prediction_id):
        result = get_prediction_status(prediction_id)
        return Response(result)
