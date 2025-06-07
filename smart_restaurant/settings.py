# 默认配置文件 - 自动导入开发环境设置
import os

# 根据环境变量选择配置
environment = os.getenv('DJANGO_ENV', 'development')

if environment == 'production':
    from .settings.production import *
elif environment == 'testing':
    from .settings.testing import *
else:
    # 默认使用开发环境配置
    from .settings.development import *

# 打印当前使用的配置环境（仅在调试模式下）
if DEBUG:
    print(f"🔧 Django配置: {environment.upper()} 环境")
    print(f"🔍 DEBUG: {DEBUG}")
    print(f"📍 ALLOWED_HOSTS: {ALLOWED_HOSTS}") 