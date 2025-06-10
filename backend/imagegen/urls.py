from django.urls import path
from .views import GenerateImageView, ImageStatusView

urlpatterns = [
    path("generate/", GenerateImageView.as_view(), name="generate-image"),
    path("status/<str:prediction_id>/", ImageStatusView.as_view(), name="image-status"),
]
