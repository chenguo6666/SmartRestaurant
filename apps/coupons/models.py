from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Coupon(models.Model):
    """优惠券模型"""
    
    TYPE_CHOICES = [
        ('fixed_amount', '固定金额'),
        ('percentage', '百分比折扣'),
        ('free_shipping', '免配送费'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='优惠券ID')
    name = models.CharField(max_length=100, verbose_name='优惠券名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='优惠券代码')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='优惠券类型')
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='优惠值'
    )
    min_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name='最小订单金额'
    )
    max_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='最大优惠金额'
    )
    total_quantity = models.IntegerField(verbose_name='发放总数量')
    used_quantity = models.IntegerField(default=0, verbose_name='已使用数量')
    per_user_limit = models.IntegerField(default=1, verbose_name='每用户限用次数')
    start_time = models.DateTimeField(verbose_name='有效期开始时间')
    end_time = models.DateTimeField(verbose_name='有效期结束时间')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    description = models.TextField(blank=True, null=True, verbose_name='使用说明')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'coupons'
        verbose_name = '优惠券'
        verbose_name_plural = '优惠券'
        ordering = ['-created_time']
        indexes = [
            models.Index(fields=['code'], name='idx_coupons_code'),
            models.Index(fields=['type'], name='idx_coupons_type'),
            models.Index(fields=['is_active'], name='idx_coupons_active'),
            models.Index(fields=['start_time', 'end_time'], name='idx_coupons_time_range'),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def is_valid(self):
        """检查优惠券是否有效"""
        now = timezone.now()
        return (
            self.is_active and
            self.start_time <= now <= self.end_time and
            self.used_quantity < self.total_quantity
        )
    
    def can_use(self, user, order_amount):
        """检查用户是否可以使用此优惠券"""
        if not self.is_valid():
            return False, "优惠券已失效或已用完"
        
        if order_amount < self.min_order_amount:
            return False, f"订单金额需满{self.min_order_amount}元"
        
        # 检查用户使用次数
        user_used_count = UserCoupon.objects.filter(
            user=user, coupon=self, status='used'
        ).count()
        
        if user_used_count >= self.per_user_limit:
            return False, f"每用户限用{self.per_user_limit}次"
        
        return True, "可以使用"
    
    def calculate_discount(self, order_amount):
        """计算优惠金额"""
        if self.type == 'fixed_amount':
            return min(self.discount_value, order_amount)
        elif self.type == 'percentage':
            discount = order_amount * (self.discount_value / 100)
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return discount
        else:  # free_shipping
            return self.discount_value
    
    def use(self):
        """使用优惠券（增加使用数量）"""
        self.used_quantity += 1
        self.save(update_fields=['used_quantity'])


class UserCoupon(models.Model):
    """用户优惠券关联模型"""
    
    STATUS_CHOICES = [
        ('unused', '未使用'),
        ('used', '已使用'),
        ('expired', '已过期'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='user_coupons', verbose_name='用户'
    )
    coupon = models.ForeignKey(
        Coupon, on_delete=models.CASCADE, related_name='user_coupons', verbose_name='优惠券'
    )
    order = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='使用的订单'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='unused', verbose_name='使用状态'
    )
    received_time = models.DateTimeField(auto_now_add=True, verbose_name='领取时间')
    used_time = models.DateTimeField(blank=True, null=True, verbose_name='使用时间')
    
    class Meta:
        db_table = 'user_coupons'
        verbose_name = '用户优惠券'
        verbose_name_plural = '用户优惠券'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'coupon'], name='uk_user_coupon'
            ),
        ]
        indexes = [
            models.Index(fields=['user'], name='idx_usercoupons_user'),
            models.Index(fields=['coupon'], name='idx_usercoupons_coupon'),
            models.Index(fields=['status'], name='idx_usercoupons_status'),
        ]
    
    def __str__(self):
        return f"{self.user.nickname} - {self.coupon.name}"
    
    def can_use(self, order_amount):
        """检查是否可以使用"""
        if self.status != 'unused':
            return False, "优惠券已使用或过期"
        
        return self.coupon.can_use(self.user, order_amount)
    
    def use(self, order):
        """使用优惠券"""
        if self.status != 'unused':
            raise ValueError("优惠券已使用或过期")
        
        self.status = 'used'
        self.order = order
        self.used_time = timezone.now()
        self.save()
        
        # 同时更新优惠券使用数量
        self.coupon.use()
    
    def mark_as_expired(self):
        """标记为过期"""
        self.status = 'expired'
        self.save(update_fields=['status'])
