from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from decimal import Decimal
from apps.common.responses import APIResponse
from .models import Coupon, UserCoupon
from .serializers import *
import logging

logger = logging.getLogger(__name__)


class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    """优惠券视图集"""
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Coupon.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """获取可用优惠券"""
        try:
            total_amount = request.query_params.get('total_amount', 0)
            total_amount = Decimal(str(total_amount))
            
            # 获取用户拥有的未使用优惠券
            user_coupons = UserCoupon.objects.filter(
                user=request.user,
                status='unused'
            ).select_related('coupon')
            
            available_coupons = []
            for user_coupon in user_coupons:
                coupon = user_coupon.coupon
                if coupon.is_active and coupon.is_valid():
                    available_coupons.append(coupon)
            
            # 序列化数据
            serializer = AvailableCouponSerializer(
                available_coupons, 
                many=True,
                context={'total_amount': total_amount}
            )
            
            return APIResponse.success(serializer.data)
            
        except Exception as e:
            logger.error(f"获取可用优惠券失败: {str(e)}")
            return APIResponse.error("获取优惠券失败")
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """验证优惠券"""
        try:
            coupon_code = request.data.get('coupon_code')
            total_amount = request.data.get('total_amount', 0)
            total_amount = Decimal(str(total_amount))
            
            if not coupon_code:
                return APIResponse.error("优惠券代码不能为空")
            
            # 查找优惠券
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            except Coupon.DoesNotExist:
                return APIResponse.error("优惠券不存在")
            
            # 检查优惠券是否有效
            if not coupon.is_valid():
                return APIResponse.error("优惠券已过期或不可用")
            
            # 检查用户是否拥有此优惠券
            user_coupon = UserCoupon.objects.filter(
                user=request.user,
                coupon=coupon,
                status='unused'
            ).first()
            
            if not user_coupon:
                return APIResponse.error("您没有此优惠券或已使用")
            
            # 检查最低消费金额
            if total_amount < coupon.min_order_amount:
                return APIResponse.error(f"订单金额需满{coupon.min_order_amount}元才可使用此优惠券")
            
            # 计算折扣金额
            discount_amount = coupon.calculate_discount(total_amount)
            
            return APIResponse.success({
                'coupon': CouponSerializer(coupon).data,
                'discount_amount': discount_amount,
                'final_amount': max(0, total_amount - discount_amount)
            })
            
        except Exception as e:
            logger.error(f"验证优惠券失败: {str(e)}")
            return APIResponse.error("验证优惠券失败")
