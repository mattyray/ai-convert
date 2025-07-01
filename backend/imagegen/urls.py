from django.urls import path
from .views import (
    GenerateImageView, 
    ImageStatusView, 
    UnlockImageView, 
    ListGeneratedImagesView,
    RandomizeImageView,
    UsageStatusView,
)

app_name = "imagegen"

urlpatterns = [
    path("generate/", GenerateImageView.as_view(), name="generate-image"),
    path("randomize/", RandomizeImageView.as_view(), name="randomize-image"),
    path("usage/", UsageStatusView.as_view(), name="usage-status"),
    path("status/<int:prediction_id>/", ImageStatusView.as_view(), name="image-status"),
    path("unlock/", UnlockImageView.as_view(), name="unlock-generation"),
    path("list/", ListGeneratedImagesView.as_view(), name="list-images"),
]