"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from dotenv import load_dotenv
from pathlib import Path
import os
import sys
import boto3
import sentry_sdk
import base64


load_dotenv()

DJANGO_ENV = os.getenv("DJANGO_ENV", "development")
APP_NAME = os.getenv("APP_NAME", "project")
########################################
##### FRONTEND ENVIRONMENT SETTINGS ####
########################################
PRODUCTION_FRONTEND_URL = os.getenv("PRODUCTION_FRONTEND_URL", None)
FRONTEND_URL = PRODUCTION_FRONTEND_URL if DJANGO_ENV == "production" and PRODUCTION_FRONTEND_URL else "http://localhost:3000"

########################################
######### AWS S3 SETTINGS #############
########################################
AWS_S3_STORAGE_BUCKET_NAME = os.getenv("AWS_S3_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_S3_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

########################################
####### GENERAL AWS SETTINGS ##########
########################################
AWS_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")


########################################
####### AWS CLOUDWATCH LOGGING #########
########################################
# Should use a key pair with an IAM user that
# specifically has write access to CW
AWS_CLOUDWATCH_ACCESS_KEY_ID = os.environ.get("AWS_CLOUDWATCH_ACCESS_KEY_ID")
AWS_CLOUDWATCH_SECRET_ACCESS_KEY = os.environ.get("AWS_CLOUDWATCH_SECRET_ACCESS_KEY")
AWS_CLOUDWATCH_LOG_GROUP_NAME = os.environ.get("AWS_CLOUDWATCH_LOG_GROUP_NAME")
AWS_CLOUDWATCH_LOG_STREAM_NAME = os.environ.get("AWS_CLOUDWATCH_LOG_STREAM_NAME", "logs")

INFO_LOG_HANDLER = {"class": "logging.StreamHandler"}
if all(
    [AWS_CLOUDWATCH_SECRET_ACCESS_KEY,
    AWS_CLOUDWATCH_ACCESS_KEY_ID,
    AWS_CLOUDWATCH_LOG_GROUP_NAME,
    DJANGO_ENV == "production"]
):
    INFO_LOG_HANDLER = {
        # Default to INFO and higher.
        # Logger using this handler may override with debug if DJANGO_LOG_LEVEL=debug
        "level": "INFO",
        "class": "watchtower.CloudWatchLogHandler",
        "boto3_client": boto3.client(
            service_name="logs",
            aws_access_key_id=AWS_CLOUDWATCH_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_CLOUDWATCH_SECRET_ACCESS_KEY,
            region_name=AWS_DEFAULT_REGION,
        ),
        "log_group": AWS_CLOUDWATCH_LOG_GROUP_NAME,
        # Should use a different stream for each environment
        "stream_name": AWS_CLOUDWATCH_LOG_STREAM_NAME
    }

########################################
####### SENTRY ERROR REPORTING #########
########################################

SENTRY_DSN = os.environ.get("SENTRY_DSN", None)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[sentry_sdk.integrations.django.DjangoIntegration()],
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )


########################################
####### DJANGO SETTINGS ###############
########################################
def random_secret_key():
    return os.urandom(24).hex()


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", random_secret_key())
DEBUG = DJANGO_ENV != "production"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost").split(",")


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "api",
    "corsheaders",  # for cross origin requests
    "ebhealthcheck.apps.EBHealthCheckConfig",  # for AWS Elastic Beanstalk health check
    "storages",  # for AWS S3 storage
    "drf_spectacular",  # for OpenAPI documentation
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "api.middleware.logging.RequestLogMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "project.wsgi.application"


########################################
####### DATABASE SETTINGS #############
########################################

if "test" in sys.argv or not all(
    [os.getenv("DB_NAME"), os.getenv("DB_USER"), os.getenv("DB_PASS"), os.getenv("DB_HOST")]
):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "digibooks_test",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASS"),
            "HOST": os.getenv("DB_HOST"),
            "PORT": "",
            "TEST": {
                "NAME": "digibooks_test",
            },
        },
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


########################################
####### INTERNATIONALIZATION ##########
########################################
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_TZ = True


########################################
####### STATIC FILES ##################
########################################
STATIC_URL = "/static/"

if not DEBUG:
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


########################################
####### REST FRAMEWORK ################
########################################

REST_FRAMEWORK = {
    # Pagination allows you to control how many objects
    # per page are returned.
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "PAGE_SIZE": 10,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        # allow browsing of API from browser
        # 'rest_framework.authentication.SessionAuthentication',
    ),
}

########################################
####### CORS SETTINGS #################
########################################
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
# CHANGE THIS FOR CURRENT PROJECT WHEN USING TEMPLATE
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://127\.0\.0\.1:3000$",
    r"^http://localhost:3000$",
    r"^https://changeme\.ai$",
    r"^http://changeme\.ai$",
    r"^https://pr.*\.changeme\.ai$",
]

CORS_ALLOW_HEADERS = [
    "accept-encoding",
    "content-type",
    "dnt",
    "origin",
    "x-csrftoken",
    "x-requested-with",
    "accept",
    "authorization",
    "baggage",
    "referer",
    "sec-ch-ua",
    "sec-ch-ua-mobile",
    "sec-ch-ua-platform",
    "sentry-trace",
    "user-agent",
]


########################################
####### LOGGING SETTINGS ##############
########################################
PRIMARY_LOGGER_NAME = "api"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        # INFO_LOG_HANDLER defined conditionally by availability of
        # AWS credentials in environment
        "info-handler": INFO_LOG_HANDLER,
        "slack": {
            "level": "ERROR",
            "class": "api.slack_handler.SlackErrorHandler",
            "webhook_url": os.environ.get("SLACK_ERROR_BACKEND_WEBHOOK", ""),
        },
    },
    # Root handler only sends WARNING logs to console.
    "root": {
        "handlers": ["info-handler"],
        "level": "WARNING",
    },
    "loggers": {
        PRIMARY_LOGGER_NAME: {
            "handlers": ["info-handler", "slack"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "django.request": {
            "handlers": ["slack"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

########################################
####### GMAIL - EMAIL SETTINGS #########
########################################

# Utilize service account for Gmail API to avoid OAuth flow
GMAIL_API_PROJECT_ID = os.environ.get("GMAIL_API_PROJECT_ID", "")
GMAIL_API_SERVICE_ACCOUNT_PRIVATE_KEY_ID = os.environ.get(
    "GMAIL_API_SERVICE_ACCOUNT_PRIVATE_KEY_ID", ""
)


def decode_private_key(pk):
    """
    Private key environment variable is B64 encoded. This function decodes it and returns it as a string.
    """

    # Add the missing padding to the base64 string
    missing_padding = len(pk) % 4
    if missing_padding:
        pk += "=" * (4 - missing_padding)
    private_key = base64.b64decode(pk).decode("utf-8")
    return private_key


GMAIL_API_SERVICE_ACCOUNT_PRIVATE_KEY = decode_private_key(
    os.environ.get("GMAIL_API_SERVICE_ACCOUNT_PRIVATE_KEY", "").replace("\\n", "\n")
)
GMAIL_API_SERVICE_ACCOUNT_CLIENT_EMAIL = os.environ.get(
    "GMAIL_API_SERVICE_ACCOUNT_CLIENT_EMAIL", ""
)
GMAIL_API_SERVICE_ACCOUNT_CLIENT_ID = os.environ.get("GMAIL_API_SERVICE_ACCOUNT_CLIENT_ID", "")
GMAIL_API_SERVICE_ACCOUNT_CLIENT_X509_CERT_URL = os.environ.get(
    "GMAIL_API_SERVICE_ACCOUNT_CLIENT_X509_CERT_URL", ""
)
SEND_FROM_EMAIL = os.environ.get("GMAIL_SEND_FROM_EMAIL", "")

########################################
####### EMAIL SETTINGS ################
########################################
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")

########################################
####### DRF SPECTACULAR SETTINGS #######
########################################

SPECTACULAR_SETTINGS = {
    "SWAGGER_UI_SETTINGS": {
        "defaultModelsExpandDepth": -1,  # This hides the schema models
    },
}

########################################
####### STRIPE SETTINGS ################
########################################
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
PREMIUM_COST_DOLLARS = float(os.environ.get("PREMIUM_COST_DOLLARS", 20))
PREMIUM_COST_CENTS = int(PREMIUM_COST_DOLLARS * 100)

########################################
####### RECAPTCHA SETTINGS #############
########################################
RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY", "")
