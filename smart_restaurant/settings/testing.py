from .base import *

DEBUG = True

# 测试数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 禁用缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# 简化密码验证
AUTH_PASSWORD_VALIDATORS = []

# 禁用日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# 测试环境邮件后端
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend' 