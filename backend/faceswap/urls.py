# Update your faceswap/urls.py to include the test endpoint

from django.urls import path
from .views import (
    FaceSwapCreateView,
    FaceSwapListView, 
    FaceSwapDetailView,
    FaceSwapStatusView,
    FaceSwapTestURLView,
    DebugGradioAPIView  # Add this import
)

app_name = "faceswap"

urlpatterns = [
    path("create/", FaceSwapCreateView.as_view(), name="create"),
    path("jobs/", FaceSwapListView.as_view(), name="list"),
    path("jobs/<int:pk>/", FaceSwapDetailView.as_view(), name="detail"),
    path("status/<int:job_id>/", FaceSwapStatusView.as_view(), name="status"),
    path("test-url/", FaceSwapTestURLView.as_view(), name="test-url"),
    path("debug/", DebugGradioAPIView.as_view(), name="debug"),  # Add this line
]