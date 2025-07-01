# django_project/celery_urls.py
# Minimal URL configuration for Celery workers (bypasses admin)

from django.urls import path
from django.http import JsonResponse

def celery_health_check(request):
    """Simple health check for Celery workers"""
    return JsonResponse({
        "status": "celery_worker_healthy",
        "service": "celery",
        "message": "Celery worker URLs loaded successfully"
    })

# Minimal URL patterns that don't require admin or complex routing
urlpatterns = [
    path("health/", celery_health_check, name="celery-health"),
]