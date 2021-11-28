import os
from typing import List

from django.conf.locale.de import formats as de_formats
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "v)0*5c7_&(5k#qh4*-wps&90jwoxn2%e#(42_1qk5qp19wnf6#"  # nosec: not used in production

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS: List[str] = []

# Login URLs
LOGIN_URL = "/login/"
LOGOUT_URL = "/logout/"
LOGIN_REDIRECT_URL_FAILURE = "/login/failed"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Application definition
INSTALLED_APPS = [
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_bootstrap5",
    "active_link",
    "django.contrib.humanize",
    "rest_framework",
    "ratings",
    "challenges",
    "common",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "rallyetool.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "rallyetool.wsgi.application"

# Auth
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# APi
API = False
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly",
    ],
}

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = "en"
LANGUAGES = (
    ("de", _("German")),
    ("en", _("English")),
)
LOCALE_NAME = "de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_L10N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True
LOCALE_PATHS = ["locale"]

de_formats.DATETIME_FORMAT = "d.m.Y H:i:s"
de_formats.DATE_FORMAT = "d.m.Y"
de_formats.SHORT_DATE_FORMAT = "d.m."

MODELTRANSLATION_TRANSLATION_FILES = ("ratings.translation",)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "staticfiles/"),
    os.path.join(BASE_DIR, "node_modules/"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATIC_URL = "/static/"

# Database stuff

# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    },
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
