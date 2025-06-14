from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class FaceSwapJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source_image = models.ImageField(upload_to='faceswap/source/')
    target_image = models.ImageField(upload_to='faceswap/target/')
    result_image = models.ImageField(upload_to='faceswap/results/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"FaceSwap Job {self.id} - {self.user.email} - {self.status}"