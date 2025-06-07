from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Order, OrderItem
from apps.dishes.models import Dish
from apps.dishes.serializers import DishSimpleSerializer
from apps.coupons.models import Coupon

User = get_user_model()


class OrderItemSerializer(serializers.ModelSerializer):
    """订单项序列化器"""
    dish = DishSimpleSerializer(read_only=True)
    dish_name = serializers.CharField(source='dish.name', read_only=True)
    dish_price = serializers.DecimalField(source='dish.price', max_digits=10, decimal_places=2, read_only=True)
    dish_image = serializers.CharField(source='dish.image_url', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'dish', 'dish_name', 'dish_price', 'dish_image',
            'quantity', 'special_requests', 'subtotal'
        ]

    def get_subtotal(self, obj):
        """计算订单项小计"""
        return obj.quantity * obj.dish.price


class OrderListSerializer(serializers.ModelSerializer):
    """订单列表序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    item_count = serializers.SerializerMethodField()
    items_preview = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_no', 'status', 'status_display',
            'payment_status', 'payment_status_display',
            'total_amount', 'discount_amount', 'final_amount',
            'table_number', 'created_time', 'item_count', 'items_preview'
        ]

    def get_item_count(self, obj):
        """获取商品总数量"""
        return sum(item.quantity for item in obj.items.all())

    def get_items_preview(self, obj):
        """获取商品预览信息"""
        items = obj.items.select_related('dish')[:3]
        return [f"{item.dish.name} x{item.quantity}" for item in items]


class OrderDetailSerializer(serializers.ModelSerializer):
    """订单详情序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    coupon_name = serializers.CharField(source='coupon.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_no', 'user_nickname', 'status', 'status_display',
            'payment_status', 'payment_status_display',
            'total_amount', 'discount_amount', 'final_amount',
            'table_number', 'customer_notes', 'admin_notes',
            'coupon_name', 'estimated_time',
            'created_time', 'paid_time', 'completed_time', 'cancelled_time',
            'items'
        ]


class CreateOrderSerializer(serializers.Serializer):
    """创建订单序列化器"""
    cart_items = serializers.ListField(
        child=serializers.DictField(),
        help_text='购物车商品列表'
    )
    table_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    customer_notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    def validate_cart_items(self, value):
        """验证购物车数据"""
        if not value:
            raise serializers.ValidationError('购物车不能为空')
        
        for item in value:
            if 'dish_id' not in item:
                raise serializers.ValidationError('缺少dish_id字段')
            if 'quantity' not in item:
                raise serializers.ValidationError('缺少quantity字段')
            if not isinstance(item['quantity'], int) or item['quantity'] <= 0:
                raise serializers.ValidationError('数量必须为正整数')
                
            # 验证菜品是否存在
            try:
                dish = Dish.objects.get(id=item['dish_id'], is_active=True)
                if not dish.is_in_stock():
                    raise serializers.ValidationError(f'菜品{dish.name}暂时缺货')
                if dish.stock_quantity != -1 and dish.stock_quantity < item['quantity']:
                    raise serializers.ValidationError(f'菜品{dish.name}库存不足')
            except Dish.DoesNotExist:
                raise serializers.ValidationError(f'菜品{item["dish_id"]}不存在或已下架')
        
        return value

    def validate_coupon_code(self, value):
        """验证优惠券"""
        if value:
            try:
                coupon = Coupon.objects.get(code=value, is_active=True)
                if not coupon.is_valid():
                    raise serializers.ValidationError('优惠券已过期或不可用')
            except Coupon.DoesNotExist:
                raise serializers.ValidationError('优惠券不存在')
        return value


class UpdateOrderStatusSerializer(serializers.Serializer):
    """更新订单状态序列化器"""
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)


class CancelOrderSerializer(serializers.Serializer):
    """取消订单序列化器"""
    reason = serializers.CharField(max_length=200, required=False, allow_blank=True) 