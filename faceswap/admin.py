from django.contrib import admin
from .models import FaceSwapJob

@admin.register(FaceSwapJob)
class FaceSwapJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'completed_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return self.readonly_fields + ['user', 'source_image', 'target_image']
        return self.readonly_fields