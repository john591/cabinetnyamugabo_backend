import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
IS_RENDER = os.getenv("RENDER", "").lower() == "true" or bool(
    os.getenv("RENDER_EXTERNAL_HOSTNAME")
)
if not IS_RENDER:
    load_dotenv(BASE_DIR / ".env")


def get_env_list(name, default=None):
    value = os.getenv(name)
    if value is None:
        return default or []
    return [item.strip() for item in value.split(",") if item.strip()]


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-dev-key-change-me")
DEBUG_DEFAULT = "False" if IS_RENDER else "True"
DEBUG = os.getenv("DJANGO_DEBUG", DEBUG_DEFAULT).lower() in {"1", "true", "yes", "on"}
ALLOWED_HOSTS = get_env_list(
    "DJANGO_ALLOWED_HOSTS",
    ["127.0.0.1", "localhost", "testserver"],
)
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "account",
    "api",
    "appointment",
    "blog",
    "contact",
    "core",
    "services",
    "team",
]

USE_S3 = os.getenv("DJANGO_USE_S3", "False").lower() in {"1", "true", "yes", "on"}
if USE_S3:
    INSTALLED_APPS.append("storages")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cabinetnyamugabo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "cabinetnyamugabo.wsgi.application"

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
else:
    sqlite_name = os.getenv("DJANGO_DB_NAME", str(BASE_DIR / "db.sqlite3"))
    if IS_RENDER:
        sqlite_name = str(BASE_DIR / "db.sqlite3")
    DATABASES = {
        "default": {
            "ENGINE": os.getenv("DJANGO_DB_ENGINE", "django.db.backends.sqlite3"),
            "NAME": sqlite_name,
            "USER": os.getenv("DJANGO_DB_USER", ""),
            "PASSWORD": os.getenv("DJANGO_DB_PASSWORD", ""),
            "HOST": os.getenv("DJANGO_DB_HOST", ""),
            "PORT": os.getenv("DJANGO_DB_PORT", ""),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = os.getenv("DJANGO_LANGUAGE_CODE", "en-us")
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "Africa/Kinshasa")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "")
AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN", "")
AWS_S3_SIGNATURE_VERSION = os.getenv("AWS_S3_SIGNATURE_VERSION", "s3v4")
AWS_DEFAULT_ACL = os.getenv("AWS_DEFAULT_ACL") or None
AWS_QUERYSTRING_AUTH = os.getenv("AWS_QUERYSTRING_AUTH", "False").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
AWS_S3_FILE_OVERWRITE = os.getenv("AWS_S3_FILE_OVERWRITE", "False").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

if USE_S3:
    media_domain = AWS_S3_CUSTOM_DOMAIN or (
        f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
        if AWS_STORAGE_BUCKET_NAME and AWS_S3_REGION_NAME
        else f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    )
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "bucket_name": AWS_STORAGE_BUCKET_NAME,
                "region_name": AWS_S3_REGION_NAME,
                "default_acl": AWS_DEFAULT_ACL,
                "querystring_auth": AWS_QUERYSTRING_AUTH,
                "file_overwrite": AWS_S3_FILE_OVERWRITE,
                "object_parameters": AWS_S3_OBJECT_PARAMETERS,
            },
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    MEDIA_URL = f"https://{media_domain}/"
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("JWT_ACCESS_MINUTES", "60"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.getenv("JWT_REFRESH_DAYS", "7"))
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

CORS_ALLOWED_ORIGINS = get_env_list(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    [
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "https://cabinenyamugabo.vercel.app",

    ],
)
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = get_env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    [
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "https://cabinenyamugabo.vercel.app",
    ],
)
DEFAULT_FRONTEND_BASE_URL = os.getenv(
    "DEFAULT_FRONTEND_BASE_URL",
    "https://cabinenyamugabo.vercel.app",
)
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "")
if (
    not FRONTEND_BASE_URL
    or FRONTEND_BASE_URL.startswith("http://127.0.0.1")
    or FRONTEND_BASE_URL.startswith("http://localhost")
):
    FRONTEND_BASE_URL = DEFAULT_FRONTEND_BASE_URL
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.getenv("DJANGO_SECURE_SSL_REDIRECT", str(not DEBUG)).lower() in {
    "1",
    "true",
    "yes",
    "on",
}
SESSION_COOKIE_SECURE = os.getenv("DJANGO_SESSION_COOKIE_SECURE", str(not DEBUG)).lower() in {
    "1",
    "true",
    "yes",
    "on",
}
CSRF_COOKIE_SECURE = os.getenv("DJANGO_CSRF_COOKIE_SECURE", str(not DEBUG)).lower() in {
    "1",
    "true",
    "yes",
    "on",
}
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    "False",
).lower() in {"1", "true", "yes", "on"}
SECURE_HSTS_PRELOAD = os.getenv("DJANGO_SECURE_HSTS_PRELOAD", "False").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "25"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "False").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "10"))
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@example.com")
CONTACT_NOTIFICATION_EMAILS = get_env_list("CONTACT_NOTIFICATION_EMAILS")
APPOINTMENT_NOTIFICATION_EMAILS = get_env_list(
    "APPOINTMENT_NOTIFICATION_EMAILS",
    CONTACT_NOTIFICATION_EMAILS,
)
APPOINTMENT_CONFIRMATION_SUBJECT = os.getenv(
    "APPOINTMENT_CONFIRMATION_SUBJECT",
    "Demande de rendez-vous reçue",
)
APPOINTMENT_EMAIL_VERIFICATION_SUBJECT = os.getenv(
    "APPOINTMENT_EMAIL_VERIFICATION_SUBJECT",
    "Verify your email to complete your appointment request",
)
APPOINTMENT_EMAIL_VERIFICATION_SALT = os.getenv(
    "APPOINTMENT_EMAIL_VERIFICATION_SALT",
    "appointment-email-verification",
)
APPOINTMENT_EMAIL_VERIFICATION_MAX_AGE = int(
    os.getenv("APPOINTMENT_EMAIL_VERIFICATION_MAX_AGE", "86400")
)
APPOINTMENT_FRONTEND_VERIFY_PATH = os.getenv(
    "APPOINTMENT_FRONTEND_VERIFY_PATH",
    "/appointments/verify-email",
)

SMS_ENABLED = os.getenv("SMS_ENABLED", "False").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
SMS_PROVIDER = os.getenv("SMS_PROVIDER", "twilio")
SMS_TIMEOUT = int(os.getenv("SMS_TIMEOUT", "10"))
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "")
APPOINTMENT_SMS_CONFIRMATION_MESSAGE = os.getenv(
    "APPOINTMENT_SMS_CONFIRMATION_MESSAGE",
    "Cabinet Nyamugabo: Dear {name}, we received your appointment request for {preferred_date} at {preferred_time} in {office}. We will contact you to confirm.",
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
