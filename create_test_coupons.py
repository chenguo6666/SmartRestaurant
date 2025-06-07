#!/usr/bin/env python
"""
创建测试优惠券数据
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_restaurant.settings.development')
django.setup()

from apps.coupons.models import Coupon, UserCoupon
from apps.users.models import User
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

def create_test_coupons():
    """创建测试优惠券"""
    
    # 创建测试优惠券
    if not Coupon.objects.filter(code='TEST10').exists():
        coupon1 = Coupon.objects.create(
            name='新用户10元券',
            code='TEST10',
            description='满50元可用',
            type='fixed_amount',
            discount_value=Decimal('10.00'),
            min_order_amount=Decimal('50.00'),
            total_quantity=100,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=30),
            is_active=True
        )
        print(f'✅ 创建优惠券: {coupon1.name}')

    if not Coupon.objects.filter(code='SAVE20').exists():
        coupon2 = Coupon.objects.create(
            name='满100减20',
            code='SAVE20', 
            description='满100元减20元',
            type='fixed_amount',
            discount_value=Decimal('20.00'),
            min_order_amount=Decimal('100.00'),
            total_quantity=50,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=15),
            is_active=True
        )
        print(f'✅ 创建优惠券: {coupon2.name}')

    # 给用户分配优惠券
    users = User.objects.all()[:2]
    coupons = Coupon.objects.all()

    for user in users:
        for coupon in coupons:
            user_coupon, created = UserCoupon.objects.get_or_create(
                user=user,
                coupon=coupon,
                defaults={'status': 'unused'}
            )
            if created:
                print(f'✅ 给用户 {user.nickname} 分配优惠券 {coupon.name}')

    print('🎉 测试优惠券数据创建完成!')

if __name__ == '__main__':
    create_test_coupons() 