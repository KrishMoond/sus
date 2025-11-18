"""
Production settings
"""
from .base import *

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Security settings for production
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static files for production
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Email for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Logging for production
LOGGING['handlers']['file']['filename'] = '/var/log/ecoconnect/django.log'