#!/usr/bin/env python
"""
测试数据模型功能脚本
"""
import os
import sys
import django
from pathlib import Path
from decimal import Decimal
from django.utils import timezone

# 添加项目根目录到Python路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_restaurant.settings.development')
django.setup()

from apps.users.models import User
from apps.dishes.models import Category, Dish
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment
from apps.coupons.models import Coupon, UserCoupon
from apps.reviews.models import Review


def test_user_model():
    """测试用户模型"""
    print("🧪 测试用户模型...")
    
    # 获取测试用户
    user = User.objects.get(openid='test_user_001')
    print(f"✅ 用户信息: {user.nickname} ({user.openid})")
    print(f"   手机号: {user.phone}")
    print(f"   性别: {user.get_gender_display()}")
    print(f"   是否激活: {user.is_active}")
    
    # 测试更新最后登录时间
    user.update_last_login()
    print(f"   最后登录时间: {user.last_login_time}")


def test_dish_model():
    """测试菜品模型"""
    print("\n🧪 测试菜品模型...")
    
    # 获取推荐菜品
    recommended_dishes = Dish.objects.filter(is_recommended=True)
    print(f"✅ 推荐菜品数量: {recommended_dishes.count()}")
    
    for dish in recommended_dishes:
        print(f"   {dish.name} - ¥{dish.price}")
        print(f"     分类: {dish.category.name}")
        print(f"     辣度: {dish.get_spicy_level_display()}")
        print(f"     库存状态: {'有库存' if dish.is_in_stock else '无库存'}")
        if dish.original_price:
            print(f"     折扣率: {dish.discount_rate}%")


def test_order_model():
    """测试订单模型"""
    print("\n🧪 测试订单模型...")
    
    # 创建测试订单
    user = User.objects.get(openid='test_user_001')
    dish1 = Dish.objects.get(name='宫保鸡丁')
    dish2 = Dish.objects.get(name='白米饭')
    
    # 创建订单
    order = Order.objects.create(
        user=user,
        total_amount=Decimal('41.00'),
        final_amount=Decimal('41.00'),
        table_number='A01',
        customer_notes='少辣，多放花生'
    )
    
    # 创建订单项
    OrderItem.objects.create(
        order=order,
        dish=dish1,
        dish_name=dish1.name,
        dish_price=dish1.price,
        quantity=1,
        dish_image_url=dish1.image_url,
        special_requests='少辣'
    )
    
    OrderItem.objects.create(
        order=order,
        dish=dish2,
        dish_name=dish2.name,
        dish_price=dish2.price,
        quantity=1
    )
    
    print(f"✅ 创建订单: {order.order_no}")
    print(f"   用户: {order.user.nickname}")
    print(f"   桌号: {order.table_number}")
    print(f"   总金额: ¥{order.total_amount}")
    print(f"   状态: {order.get_status_display()}")
    print(f"   订单项数量: {order.items.count()}")
    
    for item in order.items.all():
        print(f"     - {item.dish_name} x {item.quantity} = ¥{item.subtotal}")
    
    # 测试订单状态变更
    print(f"   可以支付: {order.can_pay()}")
    print(f"   可以取消: {order.can_cancel()}")
    
    return order


def test_payment_model(order):
    """测试支付模型"""
    print("\n🧪 测试支付模型...")
    
    # 创建支付记录
    payment = Payment.objects.create(
        order=order,
        payment_method='wechat_pay',
        amount=order.final_amount
    )
    
    print(f"✅ 创建支付: {payment.payment_no}")
    print(f"   支付方式: {payment.get_payment_method_display()}")
    print(f"   支付金额: ¥{payment.amount}")
    print(f"   支付状态: {payment.get_status_display()}")
    
    # 模拟支付成功
    payment.mark_as_success(third_party_id='wx_123456789')
    print(f"   支付成功，订单状态: {order.get_status_display()}")
    
    return payment


def test_coupon_model():
    """测试优惠券模型"""
    print("\n🧪 测试优惠券模型...")
    
    user = User.objects.get(openid='test_user_002')
    coupon = Coupon.objects.get(code='NEWUSER10')
    
    print(f"✅ 优惠券: {coupon.name}")
    print(f"   类型: {coupon.get_type_display()}")
    print(f"   优惠值: ¥{coupon.discount_value}")
    print(f"   最小订单金额: ¥{coupon.min_order_amount}")
    print(f"   是否有效: {coupon.is_valid()}")
    
    # 测试用户是否可以使用
    can_use, message = coupon.can_use(user, Decimal('60.00'))
    print(f"   用户可以使用: {can_use} - {message}")
    
    # 计算优惠金额
    discount = coupon.calculate_discount(Decimal('60.00'))
    print(f"   优惠金额: ¥{discount}")
    
    # 用户领取优惠券
    user_coupon, created = UserCoupon.objects.get_or_create(
        user=user,
        coupon=coupon
    )
    
    if created:
        print(f"   用户领取优惠券成功")
    else:
        print(f"   用户已领取过此优惠券")


def test_review_model():
    """测试评价模型"""
    print("\n🧪 测试评价模型...")
    
    user = User.objects.get(openid='test_user_003')
    dish = Dish.objects.get(name='宫保鸡丁')
    
    # 创建菜品评价
    review = Review.objects.create(
        user=user,
        dish=dish,
        rating=5,
        content='味道很棒，鸡肉嫩滑，花生香脆，非常好吃！',
        is_anonymous=False
    )
    
    print(f"✅ 创建评价: {review}")
    print(f"   评分: {review.rating}星")
    print(f"   内容: {review.content}")
    print(f"   是否匿名: {review.is_anonymous}")
    
    # 商家回复
    review.reply('感谢您的好评，我们会继续努力！')
    print(f"   商家回复: {review.reply_content}")


def main():
    """主测试函数"""
    print("🚀 开始测试数据模型功能...\n")
    
    try:
        test_user_model()
        test_dish_model()
        order = test_order_model()
        test_payment_model(order)
        test_coupon_model()
        test_review_model()
        
        print("\n🎉 所有模型测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main() 