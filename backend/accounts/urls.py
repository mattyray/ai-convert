from django.urls import path
from .views import SignupAPIView, UserProfileAPIView

app_name = "accounts"

urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"),
    path("me/", UserProfileAPIView.as_view(), name="user-profile"),
]
