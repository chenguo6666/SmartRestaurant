#!/usr/bin/env python3
"""
菜品API测试脚本
用于测试菜品和分类相关的API接口功能
"""

import requests
import json
from datetime import datetime

# 基础配置
BASE_URL = 'http://127.0.0.1:8000/api'
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def print_result(title, response):
    """打印测试结果"""
    print(f"\n{'='*50}")
    print(f"测试: {title}")
    print(f"状态码: {response.status_code}")
    print(f"响应时间: {datetime.now()}")
    
    try:
        data = response.json()
        print(f"响应内容: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"响应内容: {response.text}")
    print('='*50)

def test_api_status():
    """测试API状态"""
    try:
        response = requests.get('http://127.0.0.1:8000/', headers=headers)
        print_result("API状态检查", response)
        return response.status_code == 200
    except Exception as e:
        print(f"API状态检查失败: {e}")
        return False

def test_category_list():
    """测试分类列表API"""
    try:
        response = requests.get(f'{BASE_URL}/categories/', headers=headers)
        print_result("分类列表", response)
        return response.status_code == 200
    except Exception as e:
        print(f"分类列表测试失败: {e}")
        return False

def test_dish_list():
    """测试菜品列表API"""
    try:
        response = requests.get(f'{BASE_URL}/dishes/', headers=headers)
        print_result("菜品列表", response)
        return response.status_code == 200
    except Exception as e:
        print(f"菜品列表测试失败: {e}")
        return False

def test_dish_search():
    """测试菜品搜索API"""
    try:
        # 测试搜索功能
        response = requests.get(f'{BASE_URL}/dishes/search/?keyword=牛肉', headers=headers)
        print_result("菜品搜索", response)
        return response.status_code == 200
    except Exception as e:
        print(f"菜品搜索测试失败: {e}")
        return False

def test_recommended_dishes():
    """测试推荐菜品API"""
    try:
        response = requests.get(f'{BASE_URL}/dishes/recommended/', headers=headers)
        print_result("推荐菜品", response)
        return response.status_code == 200
    except Exception as e:
        print(f"推荐菜品测试失败: {e}")
        return False

def test_hot_dishes():
    """测试热销菜品API"""
    try:
        response = requests.get(f'{BASE_URL}/dishes/hot/', headers=headers)
        print_result("热销菜品", response)
        return response.status_code == 200
    except Exception as e:
        print(f"热销菜品测试失败: {e}")
        return False

def test_dish_filters():
    """测试菜品筛选功能"""
    try:
        # 测试分类筛选
        response = requests.get(f'{BASE_URL}/dishes/?category=1', headers=headers)
        print_result("分类筛选", response)
        
        # 测试价格筛选
        response = requests.get(f'{BASE_URL}/dishes/?min_price=10&max_price=50', headers=headers)
        print_result("价格筛选", response)
        
        # 测试搜索筛选
        response = requests.get(f'{BASE_URL}/dishes/?search=面', headers=headers)
        print_result("搜索筛选", response)
        
        return True
    except Exception as e:
        print(f"菜品筛选测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试菜品API接口...")
    
    # 测试用例列表
    tests = [
        ("API状态检查", test_api_status),
        ("分类列表API", test_category_list),
        ("菜品列表API", test_dish_list),
        ("菜品搜索API", test_dish_search),
        ("推荐菜品API", test_recommended_dishes),
        ("热销菜品API", test_hot_dishes),
        ("菜品筛选功能", test_dish_filters),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n开始测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}: {'通过' if result else '失败'}")
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ {test_name}: 测试异常 - {e}")
    
    # 输出测试总结
    print(f"\n{'='*60}")
    print("测试总结")
    print('='*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！菜品API功能正常")
    else:
        print("\n⚠️ 部分测试失败，请检查API配置")

if __name__ == '__main__':
    main() 