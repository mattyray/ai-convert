from django.urls import path
from .views import (
    FaceSwapCreateView,
    FaceSwapListView, 
    FaceSwapDetailView,
    FaceSwapStatusView,
)

app_name = "faceswap"

urlpatterns = [
    path("create/", FaceSwapCreateView.as_view(), name="create"),
    path("jobs/", FaceSwapListView.as_view(), name="list"),
    path("jobs/<int:pk>/", FaceSwapDetailView.as_view(), name="detail"),
    path("status/<int:job_id>/", FaceSwapStatusView.as_view(), name="status"),
]