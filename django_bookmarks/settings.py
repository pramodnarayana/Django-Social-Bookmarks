"""
Django settings for django_bookmarks project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e9)(kg(*9ncz#!a4ehhcy0h$2kb9e!g(h14bz4h(=i0n6lcgi^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SITE_ID = 1

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

SITE_HOST = 'kitewalk.com'
EMAIL_HOST = 'smtp.gmail.com'
DEFAULT_FROM_EMAIL = 'pramod.narayana@gmail.com'
EMAIL_HOST_USER = 'pramod.narayana@gmail.com'
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.comments',
    'bookmarks',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR,  'templates'),
)

ROOT_URLCONF = 'django_bookmarks.urls'

WSGI_APPLICATION = 'django_bookmarks.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'bookmarksdb'),
    }
}
'''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bookmarksdb',
        'USER': 'pramod',
        'PASSWORD': 'pramod',
        'HOST': 'localhost',
        'PORT': 3306
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

import django.contrib.auth
LOGIN_URL = '/login/'

