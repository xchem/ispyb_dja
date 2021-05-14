from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7!%=0w@rmjou1bo63u81$57u8^x%snfz&*11@l&3+&&824cm5e'

# You will need to change database credentials to match the database you are hooking into
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("POSTGRESQL_DATABASE", "ispyb-dja"),
        "USER": os.environ.get("POSTGRESQL_USER", "ispyb-dja"),
        "PASSWORD": os.environ.get("POSTGRESQL_PASSWORD", "ispyb-dja"),
        "HOST": os.environ.get("POSTGRESQL_HOST", "ispyb-dja-db"),
        "PORT": os.environ.get("POSTGRESQL_PORT", 5432),
    }
}

if os.environ.get('GITHUB_WORKFLOW'):
    DATABASES = {
        'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'github_actions',
           'USER': 'postgres',
           'PASSWORD': 'postgres',
           'HOST': '127.0.0.1',
           'PORT': '5432',
        }
    }

# Application definition
INSTALLED_APPS = [
    "django_auth",
    "django_dbconn_retry",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "django_cas_ng",
    "guardian"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'django_auth.wsgi.application'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG_AUTH", "False")

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
ALLOWED_HOSTS = ["*"]


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

ROOT_URLCONF = "django_auth.urls"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "static")
STATIC_URL = "/static/"

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

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_SECURE = False

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# CAS parameters
CAS_SERVER_URL = "https://auth.diamond.ac.uk:443/cas/"
CAS_REDIRECT_URL = "/"
CAS_FORCE_CHANGE_USERNAME_CASE = "lower"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "django_cas_ng.backends.CASBackend",
    "guardian.backends.ObjectPermissionBackend",
)

LOGIN_URL = "/accounts/login/"
LOGOUT_URL = "/accounts/logout/"