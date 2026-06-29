import hashlib
from django.conf import settings

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