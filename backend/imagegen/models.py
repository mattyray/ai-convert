from django.db import models
from django.conf import settings

class GeneratedImage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_images"
    )
    prompt = models.TextField()
    match_name = models.CharField(max_length=100)
    selfie = models.ImageField(upload_to="uploads/selfies/")
    output_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.match_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
