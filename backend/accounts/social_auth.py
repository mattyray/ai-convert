from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
import requests
import json
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

User = get_user_model()

class GoogleAuthView(APIView):
    def post(self, request):
        """Handle Google OAuth credential verification"""
        credential = request.data.get('credential')
        user_info = request.data.get('user_info', {})
        
        if not credential:
            return Response({'error': 'Google credential required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify the Google JWT token
            idinfo = id_token.verify_oauth2_token(
                credential, 
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            email = idinfo.get('email')
            if not email:
                return Response({'error': 'Email not provided by Google'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create user
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    email=email,
                    first_name=idinfo.get('given_name', ''),
                    last_name=idinfo.get('family_name', ''),
                )
            
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
            return Response({'error': f'Invalid Google token: {str(e)}'}, 
                          status=status.HTTP_400_BAD_REQUEST)

class FacebookAuthView(APIView):
    def post(self, request):
        """Handle Facebook OAuth token verification"""
        access_token = request.data.get('access_token')
        user_info = request.data.get('user_info', {})
        
        if not access_token:
            return Response({'error': 'Facebook access token required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify token with Facebook
            fb_response = requests.get(
                f'https://graph.facebook.com/me?fields=id,email,first_name,last_name&access_token={access_token}'
            )
            
            if fb_response.status_code != 200:
                return Response({'error': 'Invalid Facebook token'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            fb_data = fb_response.json()
            email = fb_data.get('email')
            
            if not email:
                return Response({'error': 'Email not provided by Facebook'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create user
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    email=email,
                    first_name=fb_data.get('first_name', ''),
                    last_name=fb_data.get('last_name', ''),
                )
            
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
            
        except Exception as e:
            return Response({'error': f'Facebook auth failed: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)