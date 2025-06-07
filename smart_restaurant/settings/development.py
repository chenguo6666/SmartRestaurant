from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# 开发环境特定配置
INSTALLED_APPS += [
    'django_extensions',
    # 'debug_toolbar',  # 暂时禁用，避免配置问题
]

# MIDDLEWARE += [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]

# CORS配置(开发环境)
CORS_ALLOW_ALL_ORIGINS = True

# Debug Toolbar配置
INTERNAL_IPS = [
    '127.0.0.1',
]

# 开发环境数据库配置（如果需要特殊配置）
# DATABASES['default']['OPTIONS']['init_command'] = "SET sql_mode='STRICT_TRANS_TABLES'" 