from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class GoogleAuthView(APIView):
    def post(self, request):
        """Simplified Google OAuth - no JWT verification needed"""
        try:
            print("🔑 Google auth request received")
            print(f"Request data keys: {list(request.data.keys())}")
            
            credential = request.data.get('credential')
            user_info = request.data.get('user_info', {})
            
            if not credential:
                print("❌ No credential provided")
                return Response({'error': 'Google credential required'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Extract email from user_info (already parsed by frontend)
            email = user_info.get('email')
            if not email:
                print("❌ No email in user_info")
                print(f"Available user_info: {user_info}")
                return Response({'error': 'Email not provided'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            print(f"✅ Processing auth for email: {email}")
            
            # Get or create user (simplified approach)
            try:
                user = User.objects.get(email=email)
                print(f"👤 Found existing user: {email}")
                
                # Update names if they're empty
                if not user.first_name and user_info.get('given_name'):
                    user.first_name = user_info.get('given_name', '')
                if not user.last_name and user_info.get('family_name'):
                    user.last_name = user_info.get('family_name', '')
                user.save()
                
            except User.DoesNotExist:
                print(f"📝 Creating new user: {email}")
                user = User.objects.create_user(
                    email=email,
                    first_name=user_info.get('given_name', ''),
                    last_name=user_info.get('family_name', ''),
                )
            
            # Create or get token
            token, created = Token.objects.get_or_create(user=user)
            print(f"🔑 Token {'created' if created else 'retrieved'} for user")
            
            response_data = {
                'token': token.key,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }
            
            print(f"✅ Sending success response for user {email}")
            return Response(response_data)
            
        except Exception as e:
            print(f"❌ Unexpected error in Google auth: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': 'Google authentication failed'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class FacebookAuthView(APIView):
    def post(self, request):
        """Facebook auth placeholder"""
        return Response({'error': 'Facebook auth not available on HTTP'}, 
                      status=status.HTTP_400_BAD_REQUEST)