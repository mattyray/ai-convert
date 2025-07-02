from django.urls import path
from .views import SignupAPIView, UserProfileAPIView, CustomAuthToken
from .social_auth import GoogleAuthView, FacebookAuthView


app_name = "accounts"

urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"),
    path("me/", UserProfileAPIView.as_view(), name="user-profile"),
    path("login/", CustomAuthToken.as_view(), name="token-login"),
    path("auth/google/", GoogleAuthView.as_view(), name="google-auth"),
    path("auth/facebook/", FacebookAuthView.as_view(), name="facebook-auth"),


]
