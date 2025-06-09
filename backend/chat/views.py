from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from openai import OpenAI
from .openai_utils import get_openai_response

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class ChatAPIView(APIView):
    """
    POST /api/chat/ask/
    Accepts a user message and returns an AI-generated reply using OpenAI.
    """

    def post(self, request, *args, **kwargs):
        message = request.data.get("message", "")
        if not message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reply = get_openai_response(message)
            return Response({"reply": reply}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
