from django.contrib import admin
from .models import GeneratedImage

@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ('match_name', 'user', 'created_at')
    readonly_fields = ('created_at',)
