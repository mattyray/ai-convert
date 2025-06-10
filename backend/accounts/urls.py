from django.urls import path
from .views import SignupAPIView, UserProfileAPIView, CustomAuthToken

app_name = "accounts"

urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"),
    path("me/", UserProfileAPIView.as_view(), name="user-profile"),
    path("login/", CustomAuthToken.as_view(), name="token-login"),
]
