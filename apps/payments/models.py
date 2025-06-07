from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid


class Payment(models.Model):
    """支付记录模型"""
    
    PAYMENT_METHOD_CHOICES = [
        ('wechat_pay', '微信支付'),
        ('alipay', '支付宝'),
        ('cash', '现金支付'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('success', '支付成功'),
        ('failed', '支付失败'),
        ('cancelled', '已取消'),
        ('refunded', '已退款'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='支付记录ID')
    order = models.ForeignKey(
        'orders.Order', on_delete=models.RESTRICT, related_name='payments', verbose_name='订单'
    )
    payment_no = models.CharField(max_length=64, unique=True, verbose_name='支付流水号')
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name='支付方式'
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='支付金额'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='支付状态'
    )
    third_party_transaction_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='第三方交易号'
    )
    prepay_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='预支付交易会话标识'
    )
    notify_data = models.JSONField(blank=True, null=True, verbose_name='支付回调通知数据')
    refund_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name='退款金额'
    )
    refund_reason = models.CharField(
        max_length=200, blank=True, null=True, verbose_name='退款原因'
    )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    paid_time = models.DateTimeField(blank=True, null=True, verbose_name='支付完成时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'payments'
        verbose_name = '支付记录'
        verbose_name_plural = '支付记录'
        ordering = ['-created_time']
        indexes = [
            models.Index(fields=['order'], name='idx_payments_order'),
            models.Index(fields=['payment_no'], name='idx_payments_payment_no'),
            models.Index(fields=['third_party_transaction_id'], name='idx_payments_third_party_id'),
            models.Index(fields=['status'], name='idx_payments_status'),
            models.Index(fields=['-created_time'], name='idx_payments_created_time'),
        ]
    
    def save(self, *args, **kwargs):
        if not self.payment_no:
            self.payment_no = self.generate_payment_no()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"支付{self.payment_no} - {self.get_status_display()}"
    
    @staticmethod
    def generate_payment_no():
        """生成支付流水号"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_str = str(uuid.uuid4().hex)[:8].upper()
        return f"PAY{timestamp}{random_str}"
    
    def mark_as_success(self, third_party_id=None, notify_data=None):
        """标记支付成功"""
        self.status = 'success'
        self.paid_time = timezone.now()
        if third_party_id:
            self.third_party_transaction_id = third_party_id
        if notify_data:
            self.notify_data = notify_data
        self.save()
        
        # 同时更新订单状态
        self.order.mark_as_paid()
    
    def mark_as_failed(self, reason=None):
        """标记支付失败"""
        self.status = 'failed'
        if reason:
            self.refund_reason = reason
        self.save()
    
    def refund(self, amount=None, reason=None):
        """退款"""
        if self.status != 'success':
            raise ValueError(f"支付{self.payment_no}状态不是成功，无法退款")
        
        refund_amount = amount or self.amount
        if refund_amount > self.amount - self.refund_amount:
            raise ValueError("退款金额超过可退款金额")
        
        self.refund_amount += refund_amount
        if reason:
            self.refund_reason = reason
        
        # 如果全额退款，更新状态
        if self.refund_amount >= self.amount:
            self.status = 'refunded'
        
        self.save()
