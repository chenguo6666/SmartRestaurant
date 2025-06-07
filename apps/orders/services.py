from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Order, OrderItem
from apps.dishes.models import Dish
from apps.coupons.models import Coupon, UserCoupon
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class OrderService:
    """订单业务服务类"""
    
    @transaction.atomic
    def create_order(self, user, order_data):
        """创建订单"""
        cart_items = order_data.get('cart_items', [])
        table_number = order_data.get('table_number', '')
        customer_notes = order_data.get('customer_notes', '')
        coupon_code = order_data.get('coupon_code', '')
        
        if not cart_items:
            raise ValueError("购物车不能为空")
        
        # 1. 验证菜品库存和状态
        dish_data = self._validate_cart_items(cart_items)
        
        # 2. 计算订单金额
        total_amount = sum(item['subtotal'] for item in dish_data)
        
        # 3. 应用优惠券
        discount_amount = Decimal('0.00')
        coupon = None
        if coupon_code:
            coupon, discount_amount = self._apply_coupon(user, coupon_code, total_amount)
        
        final_amount = total_amount - discount_amount
        
        # 4. 创建订单
        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            table_number=table_number.strip() if table_number else '',
            customer_notes=customer_notes.strip() if customer_notes else '',
            coupon=coupon
        )
        
        # 5. 创建订单项
        order_items = []
        for item_data in dish_data:
            order_item = OrderItem(
                order=order,
                dish=item_data['dish'],
                quantity=item_data['quantity'],
                special_requests=item_data.get('special_requests', '')
            )
            order_items.append(order_item)
        
        OrderItem.objects.bulk_create(order_items)
        
        # 6. 减少库存
        for item_data in dish_data:
            if item_data['dish'].stock_quantity != -1:  # -1表示无限库存
                item_data['dish'].stock_quantity -= item_data['quantity']
                item_data['dish'].save(update_fields=['stock_quantity'])
        
        # 7. 标记优惠券为已使用
        if coupon:
            self._use_coupon(user, coupon, order)
        
        logger.info(f"用户{user.nickname}创建订单{order.order_no}, 金额{final_amount}")
        return order
    
    def _validate_cart_items(self, cart_items):
        """验证购物车商品"""
        dish_data = []
        
        for item in cart_items:
            dish_id = item.get('dish_id')
            quantity = item.get('quantity', 1)
            special_requests = item.get('special_requests', '')
            
            try:
                dish = Dish.objects.get(id=dish_id, is_active=True)
            except Dish.DoesNotExist:
                raise ValueError(f"菜品{dish_id}不存在或已下架")
            
            if not dish.is_in_stock():
                raise ValueError(f"菜品{dish.name}暂时缺货")
            
            if dish.stock_quantity != -1 and dish.stock_quantity < quantity:
                raise ValueError(f"菜品{dish.name}库存不足，仅剩{dish.stock_quantity}份")
            
            subtotal = dish.price * quantity
            dish_data.append({
                'dish': dish,
                'quantity': quantity,
                'subtotal': subtotal,
                'special_requests': special_requests
            })
        
        return dish_data
    
    def _apply_coupon(self, user, coupon_code, total_amount):
        """应用优惠券"""
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
        except Coupon.DoesNotExist:
            raise ValueError("优惠券不存在")
        
        if not coupon.is_valid():
            raise ValueError("优惠券已过期或不可用")
        
        # 检查用户是否有此优惠券
        user_coupon = UserCoupon.objects.filter(
            user=user,
            coupon=coupon,
            status='unused'
        ).first()
        
        if not user_coupon:
            raise ValueError("您没有此优惠券或已使用")
        
        # 检查最低消费金额
        if total_amount < coupon.min_order_amount:
            raise ValueError(f"订单金额需满{coupon.min_order_amount}元才可使用此优惠券")
        
        # 计算折扣金额
        discount_amount = coupon.calculate_discount(total_amount)
        
        return coupon, Decimal(str(discount_amount))
    
    def _use_coupon(self, user, coupon, order):
        """使用优惠券"""
        user_coupon = UserCoupon.objects.filter(
            user=user,
            coupon=coupon,
            status='unused'
        ).first()
        
        if user_coupon:
            user_coupon.status = 'used'
            user_coupon.used_time = timezone.now()
            user_coupon.order = order
            user_coupon.save()
    
    def get_user_orders(self, user, status=None, page=1, page_size=20):
        """获取用户订单列表"""
        queryset = Order.objects.filter(user=user)
        
        if status:
            queryset = queryset.filter(status=status)
        
        queryset = queryset.prefetch_related('items__dish').order_by('-created_time')
        
        # 分页
        offset = (page - 1) * page_size
        orders = queryset[offset:offset + page_size]
        total = queryset.count()
        
        return {
            'orders': orders,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    def get_order_detail(self, order_id, user=None):
        """获取订单详情"""
        try:
            queryset = Order.objects.prefetch_related('items__dish')
            
            if user and not user.is_admin:
                # 普通用户只能查看自己的订单
                order = queryset.get(id=order_id, user=user)
            else:
                # 管理员可以查看所有订单
                order = queryset.get(id=order_id)
            
            return order
        except Order.DoesNotExist:
            return None
    
    @transaction.atomic
    def update_order_status(self, order, new_status, operator_user, notes=None):
        """更新订单状态"""
        valid_transitions = {
            'pending_payment': ['paid', 'cancelled'],
            'paid': ['preparing', 'cancelled'],
            'preparing': ['ready'],
            'ready': ['completed'],
        }
        
        if new_status not in valid_transitions.get(order.status, []):
            raise ValueError(f"订单状态不能从{order.status}变更为{new_status}")
        
        old_status = order.status
        order.status = new_status
        
        if notes:
            order.admin_notes = notes
        
        # 设置时间戳
        if new_status == 'completed':
            order.completed_time = timezone.now()
        elif new_status == 'cancelled':
            order.cancelled_time = timezone.now()
        elif new_status == 'paid':
            order.paid_time = timezone.now()
            order.payment_status = 'paid'
        
        order.save()
        
        logger.info(f"操作员{operator_user.nickname}将订单{order.order_no}状态从{old_status}更新为{new_status}")
        return order
    
    @transaction.atomic
    def cancel_order(self, order, user, reason=None):
        """取消订单"""
        if not order.can_cancel():
            raise ValueError("当前状态的订单不能取消")
        
        if order.user != user and not user.is_admin:
            raise PermissionError("只能取消自己的订单")
        
        order.status = 'cancelled'
        order.cancelled_time = timezone.now()
        if reason:
            order.customer_notes = f"{order.customer_notes}\n取消原因: {reason}" if order.customer_notes else f"取消原因: {reason}"
        
        order.save()
        
        # 恢复库存
        for item in order.items.all():
            if item.dish.stock_quantity != -1:
                item.dish.stock_quantity += item.quantity
                item.dish.save(update_fields=['stock_quantity'])
        
        # 恢复优惠券
        if order.coupon:
            self._restore_coupon(order.user, order.coupon)
        
        logger.info(f"用户{user.nickname}取消订单{order.order_no}")
        return order
    
    def _restore_coupon(self, user, coupon):
        """恢复优惠券"""
        user_coupon = UserCoupon.objects.filter(
            user=user,
            coupon=coupon,
            status='used'
        ).first()
        
        if user_coupon:
            user_coupon.status = 'unused'
            user_coupon.used_time = None
            user_coupon.order = None
            user_coupon.save() 