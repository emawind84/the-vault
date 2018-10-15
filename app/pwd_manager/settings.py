"""
Django settings for pwd_manager project.

Generated by 'django-admin startproject' using Django 2.0.9.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# You should create a new key with django.core.management.utils.get_random_secret_key()
SECRET_KEY = 't(1qwg0-^anab--n@q07u&x87!e)147-!nvh3r#m!s-b&-4uh+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # my apps
    'material.theme.teal',
    'material',
    'manager',
    'users',
    'social_django',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pwd_manager.urls'

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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'pwd_manager.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR + '/data', 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = (
    #'social_core.backends.open_id.OpenIdAuth',  # for Google authentication
    #'social_core.backends.google.GoogleOpenId',  # for Google authentication
    #'social_core.backends.google.GoogleOAuth2',  # for Google authentication
    #'social_core.backends.github.GithubOAuth2',  # for Github authentication
    #'social_core.backends.facebook.FacebookOAuth2',  # for Facebook authentication
    #'social_core.backends.kakao.KakaoOAuth2',
    #'auth.settings_backend.SettingsBackend',
    'auth.ldap_backend.LDAPBackend1',
    #'auth.ldap_backend.LDAPBackend2',
    'auth.pmis_backend.PMISBackend',
    'django.contrib.auth.backends.ModelBackend',
)

#from social_core import backends
#backends.kakao.KakaoOAuth2
#backends.google.GoogleOAuth2

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "local-static"),
]

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR + '/static'

SESSION_EXPIRE_SECONDS = 600  # 10 minutes
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True

LOGIN_URL = 'users:login'

LOGIN_REDIRECT_URL = 'manager:index'

VAULT_HOST = os.environ.get('VAULT_HOST', 'http://127.0.0.1:8200')

VAULT_TOKEN = os.environ.get('VAULT_TOKEN')

try:
    from .local_settings import *
    from .ldap_settings import *
except ImportError as err:
    print("OS error: {0}".format(err))
    pass
