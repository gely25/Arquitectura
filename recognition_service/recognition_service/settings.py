from pathlib import Path
import environ
from datetime import timedelta
import os

# ===========================
# Paths
# ===========================
BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================
# Environment variables
# ===========================
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='dev-recognition-key-change-me')
DEBUG = env('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost'])

# ===========================
# Installed apps
# ===========================
INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'recognition_service.interface.django_app.api',
]

# ===========================
# Middleware
# ===========================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ===========================
# URL conf
# ===========================
ROOT_URLCONF = 'recognition_service.urls'

# ===========================
# Templates
# ===========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Carpeta templates fuera de la app
        'DIRS': [BASE_DIR.parent / "templates"],  
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ===========================
# WSGI
# ===========================
WSGI_APPLICATION = 'recognition_service.wsgi.application'

# ===========================
# Database
# ===========================
DATABASES = {
    'default': env.db(default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
}

# ===========================
# Password validators
# ===========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===========================
# Internationalization
# ===========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ===========================
# Static & media files
# ===========================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===========================
# Default auto field
# ===========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===========================
# Django REST Framework + JWT
# ===========================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ===========================
# CORS
# ===========================
CORS_ALLOW_ALL_ORIGINS = True

# ===========================
# Opcional: ruta del modelo YOLO
# ===========================
YOLO_MODEL_PATH = env('YOLO_MODEL_PATH', default=BASE_DIR / 'model/yolo.pt')
