#!/usr/bin/env python
"""
创建初始测试数据脚本
"""
import os
import sys
import django
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

# 添加项目根目录到Python路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_restaurant.settings.development')
django.setup()

from apps.users.models import User
from apps.restaurant.models import RestaurantInfo, SystemConfig
from apps.dishes.models import Category, Dish
from apps.coupons.models import Coupon
from apps.orders.models import Order, OrderItem


def create_initial_data():
    """创建初始测试数据"""
    print("🚀 开始创建初始测试数据...")
    
    # 1. 创建餐厅信息
    print("📍 创建餐厅信息...")
    restaurant, created = RestaurantInfo.objects.get_or_create(
        id=1,
        defaults={
            'name': '智慧餐厅',
            'description': '美味佳肴，智能体验，为您提供最优质的用餐服务',
            'phone': '400-123-4567',
            'address': '北京市朝阳区智慧大厦1层',
            'business_hours': {
                'monday': {'open': '09:00', 'close': '22:00'},
                'tuesday': {'open': '09:00', 'close': '22:00'},
                'wednesday': {'open': '09:00', 'close': '22:00'},
                'thursday': {'open': '09:00', 'close': '22:00'},
                'friday': {'open': '09:00', 'close': '22:00'},
                'saturday': {'open': '09:00', 'close': '23:00'},
                'sunday': {'open': '09:00', 'close': '23:00'}
            },
            'service_charge_rate': Decimal('0.00'),
            'min_order_amount': Decimal('20.00'),
            'table_count': 50,
            'avg_meal_time': 45
        }
    )
    print(f"✅ 餐厅信息: {restaurant.name}")
    
    # 2. 创建系统配置
    print("⚙️ 创建系统配置...")
    configs = [
        ('order_timeout_minutes', '30', '订单超时时间（分钟）', 'number'),
        ('max_table_number', '50', '最大桌号', 'number'),
        ('service_start_time', '09:00', '服务开始时间', 'string'),
        ('service_end_time', '22:00', '服务结束时间', 'string'),
        ('welcome_message', '欢迎光临智慧餐厅！', '欢迎消息', 'string'),
    ]
    
    for key, value, desc, data_type in configs:
        config, created = SystemConfig.objects.get_or_create(
            config_key=key,
            defaults={
                'config_value': value,
                'description': desc,
                'data_type': data_type,
                'is_public': True
            }
        )
        print(f"✅ 系统配置: {config.config_key} = {config.config_value}")
    
    # 3. 创建菜品分类
    print("🍽️ 创建菜品分类...")
    categories_data = [
        ('招牌菜', '餐厅特色招牌菜品', 100),
        ('热菜', '各种热菜系列', 90),
        ('凉菜', '爽口凉菜系列', 80),
        ('汤品', '营养汤品系列', 70),
        ('主食', '米饭面条等主食', 60),
        ('饮品', '各种饮料茶水', 50),
    ]
    
    categories = {}
    for name, desc, sort_order in categories_data:
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={
                'description': desc,
                'sort_order': sort_order,
                'is_active': True
            }
        )
        categories[name] = category
        print(f"✅ 菜品分类: {category.name}")
    
    # 4. 创建菜品
    print("🥘 创建菜品...")
    dishes_data = [
        # 招牌菜
        ('宫保鸡丁', '招牌菜', '经典川菜，鸡肉嫩滑，花生香脆', Decimal('38.00'), Decimal('45.00'), 2, True),
        ('麻婆豆腐', '招牌菜', '正宗川味，麻辣鲜香', Decimal('28.00'), Decimal('32.00'), 3, True),
        ('红烧肉', '招牌菜', '肥而不腻，入口即化', Decimal('48.00'), None, 1, True),
        
        # 热菜
        ('糖醋里脊', '热菜', '酸甜可口，外酥内嫩', Decimal('35.00'), None, 1, False),
        ('鱼香肉丝', '热菜', '鱼香味浓，下饭神器', Decimal('32.00'), None, 2, False),
        ('青椒肉丝', '热菜', '清爽下饭，营养搭配', Decimal('25.00'), None, 1, False),
        
        # 凉菜
        ('凉拌黄瓜', '凉菜', '清脆爽口，开胃小菜', Decimal('12.00'), None, 0, False),
        ('口水鸡', '凉菜', '麻辣鲜香，口感丰富', Decimal('28.00'), None, 2, False),
        
        # 汤品
        ('西红柿鸡蛋汤', '汤品', '营养丰富，酸甜开胃', Decimal('18.00'), None, 0, False),
        ('冬瓜排骨汤', '汤品', '清淡滋补，老少皆宜', Decimal('32.00'), None, 0, False),
        
        # 主食
        ('白米饭', '主食', '优质大米，粒粒饱满', Decimal('3.00'), None, 0, False),
        ('蛋炒饭', '主食', '粒粒分明，香味扑鼻', Decimal('15.00'), None, 0, False),
        ('牛肉面', '主食', '汤浓面劲，牛肉鲜美', Decimal('25.00'), None, 1, False),
        
        # 饮品
        ('柠檬蜂蜜茶', '饮品', '清香甘甜，生津止渴', Decimal('15.00'), None, 0, False),
        ('鲜榨橙汁', '饮品', '新鲜橙子现榨，维C丰富', Decimal('18.00'), None, 0, False),
    ]
    
    for name, category_name, desc, price, original_price, spicy_level, is_recommended in dishes_data:
        dish, created = Dish.objects.get_or_create(
            name=name,
            defaults={
                'category': categories[category_name],
                'description': desc,
                'price': price,
                'original_price': original_price,
                'stock_quantity': -1,  # 无限库存
                'spicy_level': spicy_level,
                'is_recommended': is_recommended,
                'is_active': True,
                'sort_order': 100 if is_recommended else 0
            }
        )
        print(f"✅ 菜品: {dish.name} - ¥{dish.price}")
    
    # 5. 创建优惠券
    print("🎫 创建优惠券...")
    now = timezone.now()
    coupons_data = [
        ('新用户专享', 'NEWUSER10', 'fixed_amount', Decimal('10.00'), Decimal('50.00'), None, 100, 1),
        ('满减优惠', 'FULL100', 'fixed_amount', Decimal('20.00'), Decimal('100.00'), None, 50, 1),
        ('九折优惠', 'DISCOUNT90', 'percentage', Decimal('10.00'), Decimal('30.00'), Decimal('50.00'), 30, 2),
    ]
    
    for name, code, coupon_type, discount_value, min_amount, max_discount, total_qty, per_user_limit in coupons_data:
        coupon, created = Coupon.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'type': coupon_type,
                'discount_value': discount_value,
                'min_order_amount': min_amount,
                'max_discount_amount': max_discount,
                'total_quantity': total_qty,
                'per_user_limit': per_user_limit,
                'start_time': now,
                'end_time': now + timedelta(days=30),
                'is_active': True,
                'description': f'{name}，有效期30天'
            }
        )
        print(f"✅ 优惠券: {coupon.name} ({coupon.code})")
    
    # 6. 创建测试用户
    print("👤 创建测试用户...")
    test_users_data = [
        ('test_user_001', '张三', '13800138001'),
        ('test_user_002', '李四', '13800138002'),
        ('test_user_003', '王五', '13800138003'),
    ]
    
    for openid, nickname, phone in test_users_data:
        user, created = User.objects.get_or_create(
            openid=openid,
            defaults={
                'nickname': nickname,
                'phone': phone,
                'gender': 1,
                'is_active': True
            }
        )
        print(f"✅ 测试用户: {user.nickname} ({user.openid})")
    
    print("\n🎉 初始测试数据创建完成！")
    print("\n📊 数据统计:")
    print(f"   餐厅信息: {RestaurantInfo.objects.count()} 个")
    print(f"   系统配置: {SystemConfig.objects.count()} 个")
    print(f"   菜品分类: {Category.objects.count()} 个")
    print(f"   菜品数量: {Dish.objects.count()} 个")
    print(f"   优惠券: {Coupon.objects.count()} 个")
    print(f"   用户数量: {User.objects.count()} 个")


if __name__ == '__main__':
    create_initial_data() 