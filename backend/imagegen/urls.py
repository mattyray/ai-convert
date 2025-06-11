from django.urls import path
from .views import GenerateImageView, ImageStatusView, UnlockImageView

urlpatterns = [
    path("generate/", GenerateImageView.as_view(), name="generate-image"),
    path("status/<str:prediction_id>/", ImageStatusView.as_view(), name="image-status"),
    path("unlock/", UnlockImageView.as_view(), name="unlock-generation"),  # ✅ this line

]
