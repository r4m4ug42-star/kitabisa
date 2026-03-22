import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

import sys

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    '127.0.0.1,localhost,.onrender.com'
).split(',')

RENDER = 'RENDER' in os.environ
if RENDER:
    host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if host:
        ALLOWED_HOSTS.append(host)

# ==============================
# SECURITY
# ==============================

SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-key'
    else:
        raise Exception("SECRET_KEY tidak ditemukan di environment variables")

# ==============================
# APLIKASI
# ==============================

INSTALLED_APPS = [
    # Django Core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local Apps
    'kitajalan.apps.KitajalanConfig',
]


# ==============================
# MIDDLEWARE
# ==============================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==============================
# URL & WSGI
# ==============================

ROOT_URLCONF = 'kitabisa.urls'
WSGI_APPLICATION = 'kitabisa.wsgi.application'


# ==============================
# TEMPLATES
# ==============================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
            ],
        },
    },
]


# ==============================
# DATABASE
# ==============================

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}


# ==============================
# PASSWORD VALIDATION
# ==============================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==============================
# INTERNATIONALIZATION
# ==============================

LANGUAGE_CODE = 'id-id'
TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True
USE_L10N = True
USE_TZ = True


# ==============================
# STATIC FILES
# ==============================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ==============================
# MEDIA FILES
# ==============================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media' #tidak aman untuk production jangka panjang ⚠️

# Pastikan folder media dibuat
#if not os.path.exists(MEDIA_ROOT):
#    os.makedirs(MEDIA_ROOT)

# ==============================
# AUTH SETTINGS
# ==============================

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
    },
}

# ==============================
# DEFAULT PRIMARY KEY
# ==============================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================
# YOUTUBE EMBED CONFIGURATION
# ==============================

# ✅ Referrer Policy untuk YouTube embed
# 'strict-origin-when-cross-origin' adalah yang paling direkomendasikan YouTube
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Untuk development mode, kita bisa menggunakan policy yang lebih longgar
if DEBUG:
    SECURE_REFERRER_POLICY = 'no-referrer-when-downgrade'

# ✅ Trusted origins untuk CSRF (tambahkan domain Anda)
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://*.onrender.com',
]


# ✅ Allowed hosts untuk YouTube (jika perlu)
YOUTUBE_EMBED_DOMAINS = [
    'www.youtube.com',
    'youtube.com',
    'youtu.be',
    'www.youtube-nocookie.com',
    'youtube-nocookie.com',
]

# ✅ Cache settings untuk video (opsional)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'video-cache',
        'TIMEOUT': 300,  # 5 menit
    }
}


# ==============================
# SECURITY HARDENING (Production)
# ==============================

if not DEBUG:
    # Security settings untuk production
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # ✅ HTTPS settings
    #SECURE_SSL_REDIRECT = True
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True'
    SECURE_HSTS_SECONDS = 31536000  # 1 tahun
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # ✅ Referrer policy lebih ketat untuk production
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    
else:
    # Development settings
    # Untuk development, kita bisa mengizinkan frame dari YouTube
    X_FRAME_OPTIONS = 'SAMEORIGIN'


# ==============================
# CUSTOM SETTINGS
# ==============================

# ✅ Base URL (penting untuk YouTube origin parameter)
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:8000')

# ✅ Video settings
VIDEO_ALLOWED_EXTENSIONS = ['mp4', 'webm', 'ogg']
VIDEO_MAX_SIZE = 100 * 1024 * 1024  # 100MB

# ✅ YouTube API settings (jika menggunakan API)
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')
