"""
Django settings for lottery_platform project.
支持10万+用户的大规模架构配置
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_extensions',
    'silk',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.users',
    'apps.finance',
    'apps.games',
    'apps.games.lottery11x5',
    'apps.games.sports',
    'apps.games.superlotto',
    'apps.games.scratch666',
    'apps.rewards',
    'apps.core',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'silk.middleware.SilkyMiddleware',  # 性能监控
    'apps.core.performance.APIOptimizationMiddleware',  # API性能优化
    'apps.core.middleware.SecurityHeadersMiddleware',  # 安全头部
    'apps.core.middleware.RateLimitMiddleware',  # 频率限制
    'apps.core.middleware.IPWhitelistMiddleware',  # IP白名单
    'apps.core.middleware.DeviceTrackingMiddleware',  # 设备追踪
    'apps.core.middleware.RequestLoggingMiddleware',  # 请求日志
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lottery_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'lottery_platform.wsgi.application'
ASGI_APPLICATION = 'lottery_platform.asgi.application'

# Database configuration - 读写分离
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'read_replica': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # 开发环境使用同一个数据库
    }
}

# 数据库路由配置
DATABASE_ROUTERS = ['lottery_platform.db_router.DatabaseRouter']

# Cache configuration - 多层缓存策略
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        },
        'TIMEOUT': 300,  # 默认5分钟
        'KEY_PREFIX': 'lottery',
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/2'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 30},
        },
        'TIMEOUT': 3600,  # 会话缓存1小时
    },
    'api_cache': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/3'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 20},
        },
        'TIMEOUT': 180,  # API缓存3分钟
    },
    'hot_data': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/4'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 15},
        },
        'TIMEOUT': 60,  # 热点数据1分钟
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'
SESSION_COOKIE_AGE = 86400  # 24小时

# Celery configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/3')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/4')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Password validation
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

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'  # 尼日利亚时区
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}

# CORS configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

CORS_ALLOW_CREDENTIALS = True

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': '非洲彩票平台 API',
    'DESCRIPTION': '支持10万+用户的在线彩票博彩平台',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 安全防护配置
ADMIN_IP_WHITELIST = config('ADMIN_IP_WHITELIST', default='', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])

# 频率限制配置
RATE_LIMIT_ENABLE = config('RATE_LIMIT_ENABLE', default=True, cast=bool)

# 双因子认证配置
TWO_FACTOR_REQUIRED_FOR_ADMIN = config('TWO_FACTOR_REQUIRED_FOR_ADMIN', default=True, cast=bool)

# 风控系统配置
RISK_ASSESSMENT_ENABLE = config('RISK_ASSESSMENT_ENABLE', default=True, cast=bool)
FRAUD_DETECTION_ENABLE = config('FRAUD_DETECTION_ENABLE', default=True, cast=bool)

# 审计日志配置
AUDIT_LOG_RETENTION_DAYS = config('AUDIT_LOG_RETENTION_DAYS', default=90, cast=int)

# 性能优化配置
PERFORMANCE_MONITORING = {
    'ENABLE_MONITORING': config('ENABLE_PERFORMANCE_MONITORING', default=True, cast=bool),
    'SLOW_REQUEST_THRESHOLD': config('SLOW_REQUEST_THRESHOLD', default=1.0, cast=float),  # 秒
    'MAX_CONCURRENT_REQUESTS': config('MAX_CONCURRENT_REQUESTS', default=1000, cast=int),
    'MEMORY_THRESHOLD_PERCENT': config('MEMORY_THRESHOLD_PERCENT', default=80.0, cast=float),
    'ENABLE_QUERY_OPTIMIZATION': config('ENABLE_QUERY_OPTIMIZATION', default=True, cast=bool),
}

# 数据库连接池优化
DATABASE_POOL_SETTINGS = {
    'MAX_CONNECTIONS': config('DB_MAX_CONNECTIONS', default=100, cast=int),
    'CONN_MAX_AGE': config('DB_CONN_MAX_AGE', default=600, cast=int),
    'CONN_HEALTH_CHECKS': config('DB_CONN_HEALTH_CHECKS', default=True, cast=bool),
}

# API响应优化
API_OPTIMIZATION = {
    'ENABLE_COMPRESSION': config('ENABLE_API_COMPRESSION', default=True, cast=bool),
    'DEFAULT_PAGE_SIZE': config('API_DEFAULT_PAGE_SIZE', default=20, cast=int),
    'MAX_PAGE_SIZE': config('API_MAX_PAGE_SIZE', default=100, cast=int),
    'CACHE_TIMEOUT': config('API_CACHE_TIMEOUT', default=180, cast=int),
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}