from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):
    """菜品分类模型"""
    
    id = models.BigAutoField(primary_key=True, verbose_name='分类ID')
    name = models.CharField(max_length=50, verbose_name='分类名称')
    description = models.TextField(blank=True, null=True, verbose_name='分类描述')
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='分类图片URL')
    sort_order = models.IntegerField(default=0, verbose_name='排序权重')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'categories'
        verbose_name = '菜品分类'
        verbose_name_plural = '菜品分类'
        ordering = ['-sort_order', 'id']
        indexes = [
            models.Index(fields=['-sort_order'], name='idx_categories_sort'),
            models.Index(fields=['is_active'], name='idx_categories_active'),
        ]
    
    def __str__(self):
        return self.name


class Dish(models.Model):
    """菜品模型"""
    
    SPICY_LEVEL_CHOICES = [
        (0, '不辣'),
        (1, '微辣'),
        (2, '中辣'),
        (3, '重辣'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='菜品ID')
    category = models.ForeignKey(
        Category, on_delete=models.RESTRICT, related_name='dishes', verbose_name='所属分类'
    )
    name = models.CharField(max_length=100, verbose_name='菜品名称')
    description = models.TextField(blank=True, null=True, verbose_name='菜品描述')
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='价格'
    )
    original_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='原价'
    )
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='菜品主图URL')
    image_urls = models.JSONField(blank=True, null=True, verbose_name='菜品多图URLs')
    stock_quantity = models.IntegerField(default=0, verbose_name='库存数量')
    sales_count = models.IntegerField(default=0, verbose_name='销售数量')
    is_recommended = models.BooleanField(default=False, verbose_name='是否推荐菜品')
    is_active = models.BooleanField(default=True, verbose_name='是否上架')
    sort_order = models.IntegerField(default=0, verbose_name='排序权重')
    tags = models.CharField(max_length=200, blank=True, null=True, verbose_name='菜品标签')
    nutritional_info = models.JSONField(blank=True, null=True, verbose_name='营养信息')
    spicy_level = models.SmallIntegerField(
        choices=SPICY_LEVEL_CHOICES, default=0, verbose_name='辣度等级'
    )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'dishes'
        verbose_name = '菜品'
        verbose_name_plural = '菜品'
        ordering = ['-sort_order', '-sales_count', 'id']
        indexes = [
            models.Index(fields=['category'], name='idx_dishes_category'),
            models.Index(fields=['is_active'], name='idx_dishes_active'),
            models.Index(fields=['is_recommended'], name='idx_dishes_recommended'),
            models.Index(fields=['price'], name='idx_dishes_price'),
            models.Index(fields=['-sales_count'], name='idx_dishes_sales'),
            models.Index(fields=['-sort_order'], name='idx_dishes_sort'),
        ]
    
    def __str__(self):
        return f"{self.name} - ¥{self.price}"
    
    @property
    def is_in_stock(self):
        """是否有库存"""
        return self.stock_quantity == -1 or self.stock_quantity > 0
    
    @property
    def discount_rate(self):
        """折扣率"""
        if self.original_price and self.original_price > self.price:
            return round((1 - self.price / self.original_price) * 100, 1)
        return 0
    
    def decrease_stock(self, quantity):
        """减少库存"""
        if self.stock_quantity != -1:  # -1表示无限库存
            if self.stock_quantity < quantity:
                raise ValueError(f"库存不足，当前库存：{self.stock_quantity}")
            self.stock_quantity -= quantity
            self.save(update_fields=['stock_quantity'])
    
    def increase_sales(self, quantity):
        """增加销量"""
        self.sales_count += quantity
        self.save(update_fields=['sales_count'])
