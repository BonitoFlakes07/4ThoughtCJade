import hashlib
import io
import os
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, UnidentifiedImageError


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def hash_ip(ip):
    salted = f'{ip}{settings.SECRET_KEY}'
    return hashlib.sha256(salted.encode()).hexdigest()[:16]


def compress_uploaded_image(image_file):
    """Compress uploaded images while preserving their resolution."""
    if not image_file or not hasattr(image_file, 'file'):
        return image_file

    if hasattr(image_file, '_committed') and image_file._committed:
        return image_file

    try:
        image_file.file.seek(0)
        with Image.open(image_file.file) as img:
            img_format = (img.format or '').upper()
            output = io.BytesIO()

            if img_format in {'JPEG', 'JPG'}:
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                img.save(output, format='JPEG', quality=85, optimize=True, progressive=True)
                ext = '.jpg'
            elif img_format == 'PNG':
                img.save(output, format='PNG', optimize=True, compress_level=9)
                ext = '.png'
            elif img_format == 'WEBP':
                img.save(output, format='WEBP', quality=82, method=6)
                ext = '.webp'
            else:
                return image_file

            output.seek(0)
            base_name, _ = os.path.splitext(image_file.name)
            return ContentFile(output.read(), name=f'{base_name}{ext}')
    except (UnidentifiedImageError, OSError, ValueError):
        return image_file
