from rest_framework import serializers
from .models import Coupon, UserCoupon


class CouponSerializer(serializers.ModelSerializer):
    """优惠券序列化器"""
    discount_display = serializers.SerializerMethodField()
    valid_until_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'name', 'code', 'description',
            'type', 'discount_value', 'min_order_amount', 'max_discount_amount', 
            'total_quantity', 'used_quantity', 'start_time', 'end_time', 
            'discount_display', 'valid_until_display'
        ]
    
    def get_discount_display(self, obj):
        """获取优惠显示文本"""
        if obj.type == 'fixed_amount':
            return f"减{obj.discount_value}元"
        elif obj.type == 'percentage':
            return f"打{obj.discount_value}折"
        return ""
    
    def get_valid_until_display(self, obj):
        """获取有效期显示"""
        return obj.end_time.strftime('%Y-%m-%d %H:%M') if obj.end_time else ""


class UserCouponSerializer(serializers.ModelSerializer):
    """用户优惠券序列化器"""
    coupon = CouponSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = UserCoupon
        fields = [
            'id', 'coupon', 'status', 'status_display',
            'obtained_time', 'used_time', 'expired_time'
        ]


class AvailableCouponSerializer(serializers.ModelSerializer):
    """可用优惠券序列化器"""
    discount_display = serializers.SerializerMethodField()
    can_use = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'name', 'code', 'description',
            'type', 'discount_value', 'min_order_amount', 'max_discount_amount',
            'end_time', 'discount_display', 'can_use'
        ]
    
    def get_discount_display(self, obj):
        """获取优惠显示文本"""
        if obj.type == 'fixed_amount':
            return f"减{obj.discount_value}元"
        elif obj.type == 'percentage':
            return f"打{obj.discount_value}折"
        return ""
    
    def get_can_use(self, obj):
        """检查是否可以使用"""
        total_amount = self.context.get('total_amount', 0)
        return total_amount >= obj.min_order_amount 