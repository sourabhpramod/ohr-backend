# healthsync/settings.py
import os
from pathlib import Path
import environ

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env()  # reads .env

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-secret-key")
DEBUG = env("DJANGO_DEBUG", default=True)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "records",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # You can add template directories here later if needed
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


ROOT_URLCONF = "healthsync.urls"
WSGI_APPLICATION = "healthsync.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("PG_DB", default="healthsync"),
        "USER": env("PG_USER", default="healthsync"),
        "PASSWORD": env("PG_PASS", default="healthsyncpass"),
        "HOST": env("PG_HOST", default="localhost"),
        "PORT": env("PG_PORT", default=5432),
    }
}

# REST framework + JWT
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # or IsAuthenticated later
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [],  # empty = no auth
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",  # << add this
}



SPECTACULAR_SETTINGS = {
    "TITLE": "HealthSync API",
    "DESCRIPTION": "API for offline-first health records sync",
    "VERSION": "0.1.0",
}

# Celery (Redis)
CELERY_BROKER_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("REDIS_URL", default="redis://localhost:6379/0")

# Static files for dev
STATIC_URL = "/static/"

# CORS - allow local dev origins
CORS_ALLOW_ALL_ORIGINS = True

