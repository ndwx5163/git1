"""
Django settings for tiantian project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# import sys
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# sys.path.insert(0,os.path.join(BASE_DIR,"apps"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e3ioxzd5m5oz=&7*l9za+gul4v+q78^=_-h8_h1-%7^gkxnr=l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "apps.user",
    "apps.goods",
    "apps.order",
    "apps.cart",
    "tinymce",
    "haystack"
]

# 由于我们使用的user是修正后的User，所以需要重新制定，不能使用默认设置，否则迁移的时候会报错。
# 定义了之后我们创建的超级用户都会放置在数据库的user表当中
AUTH_USER_MODEL = "user.User"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tiantian.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'tiantian.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db_django_tiantian',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': 3306,
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

# 127.0.0.1:8000/static/base_no_cart.html/
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = "/home/ndwx/www/tiantian/static"

TINYMCE_DEFAULT_CONFIG = {
    "theme": "advanced",
    "width": 600,
    "height": 400,
}
EMAIL_USE_SSL = False  # 是否使用SSL加密，qq企业邮箱要求使用
EMAIL_USE_TLS = True
EMAIl_BACKED = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.163.com"
EMAIL_PORT = 25
EMAIL_HOST_USER = "ndwx5163@163.com"
EMAIL_HOST_PASSWORD = "django123"
EMAIL_FROM = "tiantian<ndwx5163@163.com>"

# 使内置的验证用户是否存在的功能可用。
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']

# 这个配置是声明缓存保存在那里。在django中 1.Database 2.Filesystem 3.Local-memory caching
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",  # cache-->redis
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# 这个是说session保存在那里，django中一共有三个选择：1.database 2.filesystem 3.cache
# 使用redis 保存session 所需要的配置.意思是，session-->cache
SESSION_ENGINE = "django.contrib.sessions.backends.cache"  # 这个默认的话是保存在mysql数据库当中
SESSION_CACHE_ALIAS = "default"

# 当你访问一个页面，并且这个页面需要登录时，而且你没有登录，而且你的视图函数使用了login_required()修饰，会自动跳转到下面的url
LOGIN_URL = "/user/login/"

# 使用了自定义的文件系统。
DEFAULT_FILE_STORAGE = 'utils.fdfs.file_storage.FDFSStorage'
NGINX_URL = 'http://192.168.0.106:8888/'
FDFS_CONF = './utils/fdfs/client.conf'

HAYSTACK_CONNECTIONS = {
    "default": {
        # "ENGINE": "haystack.backends.whoosh_backend.WhooshEngine",  # 使用whoosh引擎
        "ENGINE": "haystack.backends.jieba_whoosh_backend.WhooshEngine",  # 使用whoosh引擎
        "PATH": os.path.join(BASE_DIR, "whoosh_index"),  # 索引文件路径
    }
}
# 当添加，修改删除数据的时候，自动生成索引。
HAYSTACK_SIGNAL_PROCESSOR = "haystack.signals.RealtimeSignalProcessor"

# 搜索结果，每页返回5条，默认20条。
HATSTACK_SEARCH_RESULTS_PER_PAGE = 5
