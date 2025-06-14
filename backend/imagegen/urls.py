from django.urls import path
from .views import GenerateImageView, ImageStatusView, UnlockImageView, ListGeneratedImagesView

urlpatterns = [
    path("generate/", GenerateImageView.as_view(), name="generate-image"),
    path("status/<int:prediction_id>/", ImageStatusView.as_view(), name="image-status"),
    path("unlock/", UnlockImageView.as_view(), name="unlock-generation"),
    path("list/", ListGeneratedImagesView.as_view(), name="list-images"),  # New endpoint
]