"""
Django settings for site_engine project.

Generated by "django-admin startproject" using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from os import path, environ
from pathlib import Path

import dotenv
from django.utils.translation import gettext_lazy as _

from rating_movies.services.logging_formatters import CustomJsonFormatter


# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent


def load_env():
    dotenv.load_dotenv(BASE_DIR / ".env")


load_env()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ["SECRET_KEY"]

# SECURITY WARNING: don"t run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.flatpages",
    "ckeditor",
    "ckeditor_uploader",
    "snowpenguin.django.recaptcha3",
    "debug_toolbar",
    "rating_movies.apps.RatingMoviesConfig",
    "mailing.apps.MailingConfig",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.vk",
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
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "main_formatter": {
            "format": "{levelname} - {asctime} - {filename} - {lineno} - {message}",
            "style": "{",
        },
        "custom_formatter": {
            "()": CustomJsonFormatter,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "main_formatter",
        },
        "api_handler": {
            "class": "logging.FileHandler",
            "formatter": "custom_formatter",
            "filename": path.join("rating_movies", "logging", "api_information.log"),
        },
        "django_app_handler": {
            "class": "logging.FileHandler",
            "formatter": "custom_formatter",
            "filename": path.join("rating_movies", "logging", "django_app_information.log"),
        },
    },
    "loggers": {
        "json_api_logger": {
            "handlers": ["console", "api_handler"],
            "level": environ["DJANGO_LOG_LEVEL"],
            "propagate": True,
        },
        "json_main_logger": {
            "handlers": ["console", "django_app_handler"],
            "level": environ["DJANGO_LOG_LEVEL"],
            "propagate": True,
        },
    },
}

ROOT_URLCONF = "site_engine.urls"

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

WSGI_APPLICATION = "site_engine.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": environ["DATABASE_NAME"],
        "USER": environ["DATABASE_USER"],
        "PASSWORD": environ["DATABASE_PASSWORD"],
        "HOST": environ["DATABASE_HOST"],
        "PORT": environ["DATABASE_PORT"],
    }
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "ru"

# TIME_ZONE = "UTC"
TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = [
    ("ru", _("Russian")),
    ("en", _("English")),
]

LOCALE_PATHS = (
    BASE_DIR / "locale",
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"
STATIC_DIR = BASE_DIR / "static"
STATICFILES_DIRS = [STATIC_DIR]
# STATIC_ROOT = BASE_DIR / "static"


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"


CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_CONFIGS = {
    "default": {
        "skin": "moono",
        # "skin": "office2013",
        "toolbar_Basic": [
            ["Source", "-", "Bold", "Italic"]
        ],
        "toolbar_YourCustomToolbarConfig": [
            {"name": "document", "items": ["Source", "-", "Save", "NewPage", "Preview", "Print", "-", "Templates"]},
            {"name": "clipboard", "items": ["Cut", "Copy", "Paste", "PasteText", "PasteFromWord", "-", "Undo", "Redo"]},
            {"name": "editing", "items": ["Find", "Replace", "-", "SelectAll"]},
            {"name": "forms",
             "items": ["Form", "Checkbox", "Radio", "TextField", "Textarea", "Select", "Button", "ImageButton",
                       "HiddenField"]},
            "/",
            {"name": "basicstyles",
             "items": ["Bold", "Italic", "Underline", "Strike", "Subscript", "Superscript", "-", "RemoveFormat"]},
            {"name": "paragraph",
             "items": ["NumberedList", "BulletedList", "-", "Outdent", "Indent", "-", "Blockquote", "CreateDiv", "-",
                       "JustifyLeft", "JustifyCenter", "JustifyRight", "JustifyBlock", "-", "BidiLtr", "BidiRtl",
                       "Language"]},
            {"name": "links", "items": ["Link", "Unlink", "Anchor"]},
            {"name": "insert",
             "items": ["Image", "Flash", "Table", "HorizontalRule", "Smiley", "SpecialChar", "PageBreak", "Iframe"]},
            "/",
            {"name": "styles", "items": ["Styles", "Format", "Font", "FontSize"]},
            {"name": "colors", "items": ["TextColor", "BGColor"]},
            {"name": "tools", "items": ["Maximize", "ShowBlocks"]},
            {"name": "about", "items": ["About"]},
            "/",  # put this to force next toolbar on new line
            {"name": "yourcustomtools", "items": [
                # put the name of your editor.ui.addButton here
                "Preview",
                "Maximize",
                "Youtube",
            ]},
        ],
        "toolbar": "YourCustomToolbarConfig",  # put selected toolbar config here
        # "toolbarGroups": [{ "name": "document", "groups": [ "mode", "document", "doctools" ] }],
        # "height": 291,
        # "width": "100%",
        # "filebrowserWindowHeight": 725,
        # "filebrowserWindowWidth": 940,
        # "toolbarCanCollapse": True,
        # "mathJaxLib": "//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML",
        "tabSpaces": 4,
        "extraPlugins": ",".join([
            "uploadimage",  # the upload image feature
            # your extra plugins here
            "div",
            "autolink",
            "autoembed",
            "embedsemantic",
            "autogrow",
            # "devtools",
            "widget",
            "lineutils",
            "clipboard",
            "dialog",
            "dialogui",
            "elementspath",
            "youtube",
        ]),
    }
}

RECAPTCHA_PUBLIC_KEY = environ["RECAPTCHA_PUBLIC_KEY"]
RECAPTCHA_PRIVATE_KEY = environ["RECAPTCHA_PRIVATE_KEY"]
RECAPTCHA_DEFAULT_ACTION = "generic"
RECAPTCHA_SCORE_THRESHOLD = 0.5

SITE_ID = 1

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_USERNAME_MIN_LENGTH = 4
LOGIN_REDIRECT_URL = "/"

EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"


INTERNAL_IPS = [
    "127.0.0.1",
]


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / "rating_movies" / "rating_movies_cache",
    }
}
