from django.db import models

# Create your models here.

class RestaurantInfo(models.Model):
    """餐厅信息模型"""
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='餐厅名称')
    description = models.TextField(blank=True, null=True, verbose_name='餐厅描述')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='联系电话')
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='餐厅地址')
    business_hours = models.JSONField(blank=True, null=True, verbose_name='营业时间')
    logo_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='餐厅LOGO')
    background_images = models.JSONField(blank=True, null=True, verbose_name='背景图片URLs')
    announcement = models.TextField(blank=True, null=True, verbose_name='餐厅公告')
    service_charge_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name='服务费率（百分比）'
    )
    is_open = models.BooleanField(default=True, verbose_name='是否营业中')
    min_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name='起送金额'
    )
    table_count = models.IntegerField(default=0, verbose_name='餐桌数量')
    avg_meal_time = models.IntegerField(default=60, verbose_name='平均用餐时间（分钟）')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'restaurant_info'
        verbose_name = '餐厅信息'
        verbose_name_plural = '餐厅信息'
    
    def __str__(self):
        return self.name


class SystemConfig(models.Model):
    """系统配置模型"""
    
    DATA_TYPE_CHOICES = [
        ('string', '字符串'),
        ('number', '数字'),
        ('boolean', '布尔值'),
        ('json', 'JSON'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='配置ID')
    config_key = models.CharField(max_length=100, unique=True, verbose_name='配置键')
    config_value = models.TextField(blank=True, null=True, verbose_name='配置值')
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='配置描述')
    data_type = models.CharField(
        max_length=20, choices=DATA_TYPE_CHOICES, default='string', verbose_name='数据类型'
    )
    is_public = models.BooleanField(default=False, verbose_name='是否为公开配置')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'system_configs'
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        indexes = [
            models.Index(fields=['config_key'], name='idx_systemconfigs_key'),
            models.Index(fields=['is_public'], name='idx_systemconfigs_public'),
        ]
    
    def __str__(self):
        return f"{self.config_key}: {self.config_value}"
