from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
    # 添加您的生产域名
]

# 生产环境安全配置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_TZ = True

# CORS配置(生产环境)
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

# 生产环境日志配置
LOGGING['handlers']['file']['filename'] = '/var/log/smart_restaurant/django.log'

# 静态文件配置
STATIC_ROOT = '/var/www/smart_restaurant/static/'
MEDIA_ROOT = '/var/www/smart_restaurant/media/' 