from pathlib import Path

from . import constants as api_constants

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = api_constants.SECRET_KEY
DEBUG = api_constants.DEBUG
ALLOWED_HOSTS = api_constants.ALLOWED_HOSTS

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'shop',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api.urls'

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

WSGI_APPLICATION = 'api.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / api_constants.SQLITE_DATABASE_NAME,
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = api_constants.LANGUAGE_CODE
TIME_ZONE = api_constants.TIME_ZONE
USE_I18N = True
USE_TZ = True

STATIC_URL = api_constants.STATIC_URL
MEDIA_URL = api_constants.MEDIA_URL
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = api_constants.DEFAULT_AUTO_FIELD

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': api_constants.API_PAGE_SIZE,
}

SPECTACULAR_SETTINGS = {
    'TITLE': api_constants.SPECTACULAR_TITLE,
    'DESCRIPTION': api_constants.SPECTACULAR_DESCRIPTION,
    'VERSION': api_constants.SPECTACULAR_VERSION,
}
