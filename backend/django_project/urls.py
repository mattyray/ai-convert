from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({"message": "API is running!"})

urlpatterns = [
    path("", api_root),  # ✅ Root path now responds
    path("admin/", admin.site.urls),
    path("api/accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("api/chat/", include(("chat.urls", "chat"), namespace="chat")),
    path("api/imagegen/", include("imagegen.urls")),  # ✅ Changed from "api/image/" to "api/imagegen/"
    path("api/faceswap/", include(("faceswap.urls", "faceswap"), namespace="faceswap")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)