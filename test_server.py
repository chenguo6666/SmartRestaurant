#!/usr/bin/env python
"""
Django服务器功能测试脚本
"""
import requests
import json

def test_server_status():
    """测试服务器状态"""
    print("🧪 测试Django服务器状态...")
    
    try:
        response = requests.get('http://127.0.0.1:8000/')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务器状态: {data['status']}")
            print(f"   消息: {data['message']}")
            print(f"   版本: {data['version']}")
            return True
        else:
            print(f"❌ 服务器响应错误: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接服务器失败: {e}")
        return False

def test_admin_access():
    """测试Django Admin访问"""
    print("\n🧪 测试Django Admin后台...")
    
    try:
        response = requests.get('http://127.0.0.1:8000/admin/')
        if response.status_code == 200:
            if 'Django 站点管理员' in response.text or 'Django administration' in response.text:
                print("✅ Django Admin后台正常访问")
                return True
            else:
                print("❌ Admin页面内容异常")
                return False
        else:
            print(f"❌ Admin页面响应错误: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 访问Admin页面失败: {e}")
        return False

def test_static_files():
    """测试静态文件服务"""
    print("\n🧪 测试静态文件服务...")
    
    try:
        # 尝试访问Django Admin的CSS文件
        response = requests.get('http://127.0.0.1:8000/static/admin/css/base.css')
        if response.status_code == 200:
            print("✅ 静态文件服务正常")
            return True
        else:
            print(f"⚠️ 静态文件访问: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ 静态文件测试失败: {e}")
        return False

def test_database_connection():
    """测试数据库连接（通过Django admin检查）"""
    print("\n🧪 测试数据库连接...")
    
    try:
        # 如果admin页面能正常加载，说明数据库连接正常
        response = requests.get('http://127.0.0.1:8000/admin/auth/user/')
        if response.status_code in [200, 302]:  # 200正常，302重定向到登录页面也算正常
            print("✅ 数据库连接正常")
            return True
        else:
            print(f"❌ 数据库连接可能有问题: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始Django服务器功能测试...\n")
    
    tests = [
        test_server_status,
        test_admin_access,
        test_static_files,
        test_database_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 测试结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！Django服务器运行正常！")
        print("\n📝 接下来可以:")
        print("   - 访问 http://127.0.0.1:8000/ 查看API状态")
        print("   - 访问 http://127.0.0.1:8000/admin/ 进入管理后台")
        print("   - 开始开发API接口")
    else:
        print("❌ 部分测试失败，请检查配置")

if __name__ == '__main__':
    main() 