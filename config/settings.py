import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6(n4#mvjx6cr0*z!9k2=!4qp=&wm7m)a1%0u%lu_b92t7#l3#n'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'csp',
    'accounts',
    'tests',
    'tasks',
    'articles',
    'forum',
    'interviews',
    'comments',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',  # За замовчуванням дозволяємо доступ
    ),
    # Add date format settings for REST Framework
    'DATETIME_FORMAT': '%d.%m.%Y %H:%M',
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "https://frontender-interview-portal.netlify.app",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "https://www.youtube.com",
    "https://youtube.com",
    "https://www.googleapis.com",
    "https://googleapis.com",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Permissions-Policy',
    'browsing-topics',
    'join-ad-interest-group',
    'run-ad-auction',
]

CORS_EXPOSE_HEADERS = [
    'Content-Type',
    'Authorization',
]

# Новий формат налаштувань CSP (замість старих CSP_* налаштувань)
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'", "'unsafe-inline'", "'unsafe-eval'"),
        'frame-src': ("'self'", "https://www.youtube.com", "https://youtube.com", "https://www.youtube-nocookie.com"),
        'connect-src': ("'self'", "https://www.youtube.com", "https://youtube.com",
                      "https://www.googleapis.com", "https://googleapis.com",
                      "https://*.googlevideo.com", "https://*.ytimg.com"),
        'style-src': ("'self'", "'unsafe-inline'", "https://www.youtube.com", "https://*.ytimg.com"),
        'script-src': ("'self'", "'unsafe-inline'", "'unsafe-eval'",
                     "https://www.youtube.com", "https://youtube.com",
                     "https://www.googleapis.com", "https://googleapis.com",
                     "https://*.ytimg.com", "https://s.ytimg.com"),
        'img-src': ("'self'", "data:", "https:", "http:", "https://*.ytimg.com", "https://i.ytimg.com",
                  "https://*.googleusercontent.com", "https://*.ggpht.com"),
        'font-src': ("'self'", "data:", "https:", "http:"),
        'media-src': ("'self'", "https://*.googlevideo.com", "https://*.ytimg.com")
    }
}

# Дозволити вбудовування iframe з YouTube
X_FRAME_OPTIONS = 'SAMEORIGIN'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

AUTH_USER_MODEL = 'auth.User'

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

# Set to your local timezone (Europe/Kiev for UTC+3)
TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

# Enable timezone support
USE_TZ = True

# Format for displaying dates in Django admin/templates
DATE_FORMAT = 'd.m.Y'
DATETIME_FORMAT = 'd.m.Y H:i'
SHORT_DATETIME_FORMAT = 'd.m.Y H:i'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = 'https://frontender-media.netlify.app/'
#MEDIA_ROOT = os.path.join(BASE_DIR, 'media')