from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid


class Order(models.Model):
    """订单模型"""
    
    STATUS_CHOICES = [
        ('pending_payment', '待支付'),
        ('paid', '已支付'),
        ('preparing', '制作中'),
        ('ready', '待取餐'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', '未支付'),
        ('paid', '已支付'),
        ('refunded', '已退款'),
        ('partial_refunded', '部分退款'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='订单ID')
    order_no = models.CharField(max_length=32, unique=True, verbose_name='订单号')
    user = models.ForeignKey(
        'users.User', on_delete=models.RESTRICT, related_name='orders', verbose_name='下单用户'
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='订单总金额'
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name='优惠金额'
    )
    final_amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='实付金额'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending_payment', verbose_name='订单状态'
    )
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid', verbose_name='支付状态'
    )
    table_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='桌号')
    customer_notes = models.TextField(blank=True, null=True, verbose_name='顾客备注')
    admin_notes = models.TextField(blank=True, null=True, verbose_name='管理员备注')
    estimated_time = models.IntegerField(blank=True, null=True, verbose_name='预估完成时间（分钟）')
    coupon = models.ForeignKey(
        'coupons.Coupon', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='使用的优惠券'
    )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='下单时间')
    paid_time = models.DateTimeField(blank=True, null=True, verbose_name='支付时间')
    completed_time = models.DateTimeField(blank=True, null=True, verbose_name='完成时间')
    cancelled_time = models.DateTimeField(blank=True, null=True, verbose_name='取消时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'orders'
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_time']
        indexes = [
            models.Index(fields=['order_no'], name='idx_orders_order_no'),
            models.Index(fields=['user'], name='idx_orders_user'),
            models.Index(fields=['status'], name='idx_orders_status'),
            models.Index(fields=['payment_status'], name='idx_orders_payment_status'),
            models.Index(fields=['-created_time'], name='idx_orders_created_time'),
            models.Index(fields=['table_number'], name='idx_orders_table_number'),
        ]
    
    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = self.generate_order_no()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"订单{self.order_no} - {self.get_status_display()}"
    
    @staticmethod
    def generate_order_no():
        """生成订单号"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_str = str(uuid.uuid4().hex)[:6].upper()
        return f"ORD{timestamp}{random_str}"
    
    def can_cancel(self):
        """是否可以取消"""
        return self.status in ['pending_payment', 'paid']
    
    def can_pay(self):
        """是否可以支付"""
        return self.status == 'pending_payment' and self.payment_status == 'unpaid'
    
    def mark_as_paid(self):
        """标记为已支付"""
        self.status = 'paid'
        self.payment_status = 'paid'
        self.paid_time = timezone.now()
        self.save(update_fields=['status', 'payment_status', 'paid_time', 'updated_time'])
    
    def mark_as_completed(self):
        """标记为已完成"""
        self.status = 'completed'
        self.completed_time = timezone.now()
        self.save(update_fields=['status', 'completed_time', 'updated_time'])
    
    def cancel(self, reason=None):
        """取消订单"""
        if not self.can_cancel():
            raise ValueError(f"订单{self.order_no}当前状态不允许取消")
        
        self.status = 'cancelled'
        self.cancelled_time = timezone.now()
        if reason:
            self.admin_notes = reason
        self.save(update_fields=['status', 'cancelled_time', 'admin_notes', 'updated_time'])


class OrderItem(models.Model):
    """订单项模型"""
    
    id = models.BigAutoField(primary_key=True, verbose_name='订单项ID')
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items', verbose_name='订单'
    )
    dish = models.ForeignKey(
        'dishes.Dish', on_delete=models.RESTRICT, verbose_name='菜品'
    )
    dish_name = models.CharField(max_length=100, verbose_name='菜品名称（快照）')
    dish_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='菜品单价（快照）'
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='购买数量')
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='小计金额'
    )
    dish_image_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name='菜品图片（快照）'
    )
    special_requests = models.TextField(blank=True, null=True, verbose_name='特殊要求')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'order_items'
        verbose_name = '订单项'
        verbose_name_plural = '订单项'
        indexes = [
            models.Index(fields=['order'], name='idx_orderitems_order'),
            models.Index(fields=['dish'], name='idx_orderitems_dish'),
        ]
    
    def save(self, *args, **kwargs):
        # 自动计算小计
        self.subtotal = self.dish_price * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.dish_name} x {self.quantity}"
