# Save this as test_cloudinary_upload.py in your project root
# Run with: docker-compose exec web python test_cloudinary_upload.py

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from imagegen.models import GeneratedImage
import cloudinary.utils
from io import BytesIO
from PIL import Image

# Test Cloudinary upload
print("🧪 Testing Cloudinary upload...")

# Create a real dummy image (1x1 pixel PNG)
img = Image.new('RGB', (1, 1), color='red')
img_buffer = BytesIO()
img.save(img_buffer, format='PNG')
img_content = img_buffer.getvalue()

uploaded_file = SimpleUploadedFile(
    name="test_selfie.png",
    content=img_content,
    content_type="image/png"
)

# Create a model instance and save it
test_image = GeneratedImage(
    prompt="Test upload",
    match_name="Test",
    selfie=uploaded_file
)
test_image.save()

print(f"📁 Saved image ID: {test_image.id}")
print(f"📂 File name: {test_image.selfie.name}")
print(f"🔗 File URL: {test_image.selfie.url}")

# Try to get Cloudinary URL directly
try:
    cloudinary_url = cloudinary.utils.cloudinary_url(test_image.selfie.name)[0]
    print(f"☁️  Cloudinary URL: {cloudinary_url}")
except Exception as e:
    print(f"❌ Cloudinary URL failed: {e}")

# Check file storage
print(f"📦 Storage class: {test_image.selfie.storage.__class__.__name__}")

# Clean up
test_image.delete()
print("🧹 Cleaned up test image")