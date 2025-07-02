# imagegen/views/management_views.py - Usage tracking and image management

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from ..models import GeneratedImage, UsageSession


class UsageStatusView(APIView):
    """Get current usage status"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            return Response({"unlimited": True, "user_authenticated": True})
        
        if not request.session.session_key:
            request.session.create()
            
        usage_session = UsageSession.get_or_create_for_session(request.session.session_key)
        
        return Response({
            "matches_used": usage_session.matches_used,
            "matches_limit": usage_session.MAX_MATCHES,
            "randomizes_used": usage_session.randomizes_used,
            "randomizes_limit": usage_session.MAX_RANDOMIZES,
            "can_match": usage_session.can_match,
            "can_randomize": usage_session.can_randomize,
            "is_limited": usage_session.is_limited,
            "user_authenticated": False
        })


class ImageStatusView(APIView):
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
            return Response({"error": "Generated image not found"}, status=404)


class UnlockImageView(APIView):
    def post(self, request):
        request.session["image_generation_count"] = 0
        return Response({"message": "Unlock granted. You can generate again."})


class ListGeneratedImagesView(APIView):
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