from PIL import Image
import io
from django.core.files.base import ContentFile

def compress_image(image_file, max_size=(800, 800), quality=75):
    """Compress uploaded images to reduce memory usage"""
    try:
        img = Image.open(image_file)
        
        # Convert to RGB if necessary (removes alpha channels)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize to reasonable dimensions
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Compress
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return ContentFile(output.getvalue())
    except Exception as e:
        print(f"Compression error: {e}")
        return image_file