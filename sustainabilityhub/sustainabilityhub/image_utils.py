from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

def optimize_image(image_field, max_size=(800, 800), quality=85):
    """
    Optimize and resize uploaded images
    """
    if not image_field:
        return image_field
    
    try:
        img = Image.open(image_field)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize if larger than max_size
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Create new InMemoryUploadedFile
        return InMemoryUploadedFile(
            output,
            'ImageField',
            f"{image_field.name.split('.')[0]}.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
    except Exception as e:
        # If optimization fails, return original
        return image_field

def validate_image(image_field, max_size_mb=5):
    """
    Validate image size and type
    """
    if not image_field:
        return True, None
    
    # Check file size
    if image_field.size > max_size_mb * 1024 * 1024:
        return False, f"Image size must be less than {max_size_mb}MB"
    
    # Check file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if hasattr(image_field, 'content_type') and image_field.content_type not in allowed_types:
        return False, "Only JPEG, PNG, GIF, and WebP images are allowed"
    
    return True, None
