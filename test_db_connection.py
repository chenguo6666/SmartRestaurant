#!/usr/bin/env python
"""
数据库连接测试脚本
"""
import os
import sys
import django
from pathlib import Path

# 添加项目根目录到Python路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_restaurant.settings.development')
django.setup()

def test_database_connection():
    """测试数据库连接"""
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print("✅ 数据库连接成功！")
        print(f"测试查询结果: {result}")
        
        # 显示数据库信息
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f"当前数据库: {db_name}")
        
        cursor.execute("SELECT VERSION()")
        db_version = cursor.fetchone()[0]
        print(f"MySQL版本: {db_version}")
        
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

if __name__ == '__main__':
    print("🔍 开始测试数据库连接...")
    print("-" * 50)
    
    db_ok = test_database_connection()
    print("-" * 50)
    
    if db_ok:
        print("🎉 数据库连接测试通过！")
    else:
        print("⚠️  数据库连接测试失败，请检查配置") 