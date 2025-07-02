from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.conf import settings
import requests
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class GoogleAuthView(APIView):
    def post(self, request):
        """Handle Google OAuth credential verification - IMPROVED"""
        credential = request.data.get('credential')
        
        if not credential:
            return Response({'error': 'Google credential required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 🔥 FIXED: Better error handling and logging
            logger.info("🔑 Verifying Google credential...")
            
            # Verify the Google JWT token
            idinfo = id_token.verify_oauth2_token(
                credential, 
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID  # Use from settings
            )
            
            # 🔥 NEW: Additional validation
            if idinfo.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
                
            email = idinfo.get('email')
            if not email:
                return Response({'error': 'Email not provided by Google'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"✅ Google auth success for: {email}")
            
            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': idinfo.get('given_name', ''),
                    'last_name': idinfo.get('family_name', ''),
                }
            )
            
            if created:
                logger.info(f"📝 Created new user: {email}")
            else:
                logger.info(f"👤 Existing user login: {email}")
            
            # Create or get token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
            
        except ValueError as e:
            logger.error(f"❌ Google token validation failed: {e}")
            return Response({'error': f'Invalid Google token: {str(e)}'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"❌ Google auth error: {e}")
            return Response({'error': 'Google authentication failed'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FacebookAuthView(APIView):
    def post(self, request):
        """Handle Facebook OAuth token verification - IMPROVED"""
        access_token = request.data.get('access_token')
        
        if not access_token:
            return Response({'error': 'Facebook access token required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            logger.info("🔑 Verifying Facebook token...")
            
            # Verify token with Facebook
            fb_response = requests.get(
                f'https://graph.facebook.com/me?fields=id,email,first_name,last_name&access_token={access_token}',
                timeout=10
            )
            
            if fb_response.status_code != 200:
                logger.error(f"❌ Facebook API error: {fb_response.status_code}")
                return Response({'error': 'Invalid Facebook token'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            fb_data = fb_response.json()
            email = fb_data.get('email')
            
            if not email:
                return Response({'error': 'Email not provided by Facebook'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"✅ Facebook auth success for: {email}")
            
            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': fb_data.get('first_name', ''),
                    'last_name': fb_data.get('last_name', ''),
                }
            )
            
            if created:
                logger.info(f"📝 Created new user: {email}")
            
            # Create or get token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
            
        except requests.RequestException as e:
            logger.error(f"❌ Facebook API request failed: {e}")
            return Response({'error': 'Facebook API unavailable'}, 
                          status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            logger.error(f"❌ Facebook auth error: {e}")
            return Response({'error': 'Facebook authentication failed'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)