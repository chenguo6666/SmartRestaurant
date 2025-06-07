from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Review(models.Model):
    """评价模型"""
    
    id = models.BigAutoField(primary_key=True, verbose_name='评价ID')
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='reviews', verbose_name='评价用户'
    )
    order = models.ForeignKey(
        'orders.Order', on_delete=models.CASCADE, blank=True, null=True, 
        related_name='reviews', verbose_name='关联订单'
    )
    dish = models.ForeignKey(
        'dishes.Dish', on_delete=models.CASCADE, blank=True, null=True,
        related_name='reviews', verbose_name='关联菜品'
    )
    rating = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='评分'
    )
    content = models.TextField(blank=True, null=True, verbose_name='评价内容')
    images = models.JSONField(blank=True, null=True, verbose_name='评价图片URLs')
    is_anonymous = models.BooleanField(default=False, verbose_name='是否匿名评价')
    reply_content = models.TextField(blank=True, null=True, verbose_name='商家回复内容')
    reply_time = models.DateTimeField(blank=True, null=True, verbose_name='回复时间')
    is_visible = models.BooleanField(default=True, verbose_name='是否显示')
    helpful_count = models.IntegerField(default=0, verbose_name='有用数量')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='评价时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'reviews'
        verbose_name = '评价'
        verbose_name_plural = '评价'
        ordering = ['-created_time']
        indexes = [
            models.Index(fields=['user'], name='idx_reviews_user'),
            models.Index(fields=['order'], name='idx_reviews_order'),
            models.Index(fields=['dish'], name='idx_reviews_dish'),
            models.Index(fields=['rating'], name='idx_reviews_rating'),
            models.Index(fields=['is_visible'], name='idx_reviews_visible'),
            models.Index(fields=['-created_time'], name='idx_reviews_created_time'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(order__isnull=False) | models.Q(dish__isnull=False),
                name='chk_review_target'
            ),
        ]
    
    def __str__(self):
        target = f"订单{self.order.order_no}" if self.order else f"菜品{self.dish.name}"
        return f"{self.user.nickname}对{target}的评价"
    
    def reply(self, content):
        """商家回复"""
        self.reply_content = content
        self.reply_time = timezone.now()
        self.save(update_fields=['reply_content', 'reply_time'])
    
    def add_helpful(self):
        """增加有用数"""
        self.helpful_count += 1
        self.save(update_fields=['helpful_count'])


class Feedback(models.Model):
    """用户反馈模型"""
    
    TYPE_CHOICES = [
        ('suggestion', '建议'),
        ('complaint', '投诉'),
        ('bug_report', '问题反馈'),
        ('feature_request', '功能请求'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('closed', '已关闭'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '紧急'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='反馈ID')
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='feedbacks', verbose_name='反馈用户'
    )
    type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default='suggestion', verbose_name='反馈类型'
    )
    title = models.CharField(max_length=200, verbose_name='反馈标题')
    content = models.TextField(verbose_name='反馈内容')
    contact_info = models.CharField(
        max_length=100, blank=True, null=True, verbose_name='联系方式'
    )
    images = models.JSONField(blank=True, null=True, verbose_name='反馈图片URLs')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='处理状态'
    )
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='优先级'
    )
    admin_reply = models.TextField(blank=True, null=True, verbose_name='管理员回复')
    admin = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, blank=True, null=True,
        related_name='handled_feedbacks', verbose_name='处理的管理员'
    )
    reply_time = models.DateTimeField(blank=True, null=True, verbose_name='回复时间')
    tags = models.CharField(max_length=200, blank=True, null=True, verbose_name='标签')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='反馈时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'feedbacks'
        verbose_name = '用户反馈'
        verbose_name_plural = '用户反馈'
        ordering = ['-created_time']
        indexes = [
            models.Index(fields=['user'], name='idx_feedbacks_user'),
            models.Index(fields=['type'], name='idx_feedbacks_type'),
            models.Index(fields=['status'], name='idx_feedbacks_status'),
            models.Index(fields=['priority'], name='idx_feedbacks_priority'),
            models.Index(fields=['admin'], name='idx_feedbacks_admin'),
            models.Index(fields=['-created_time'], name='idx_feedbacks_created_time'),
        ]
    
    def __str__(self):
        return f"{self.user.nickname} - {self.title}"
    
    def assign_to_admin(self, admin_user):
        """分配给管理员处理"""
        self.admin = admin_user
        self.status = 'processing'
        self.save(update_fields=['admin', 'status'])
    
    def reply(self, content, admin_user):
        """管理员回复"""
        self.admin_reply = content
        self.admin = admin_user
        self.reply_time = timezone.now()
        self.status = 'completed'
        self.save(update_fields=['admin_reply', 'admin', 'reply_time', 'status'])
    
    def close(self):
        """关闭反馈"""
        self.status = 'closed'
        self.save(update_fields=['status'])
