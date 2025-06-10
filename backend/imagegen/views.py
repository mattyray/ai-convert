from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .replicate_utils import generate_image_from_prompt

class GenerateImageView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt")
        if not prompt:
            return Response({"error": "Prompt is required"}, status=400)

        try:
            result_url = generate_image_from_prompt(prompt)
            return Response({"status_url": result_url})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
