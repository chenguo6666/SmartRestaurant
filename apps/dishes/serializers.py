from rest_framework import serializers
from apps.common.serializers import BaseSerializer, TimestampSerializer
from .models import Category, Dish


class CategorySerializer(TimestampSerializer):
    """分类序列化器"""
    dish_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image_url', 'sort_order', 
                 'is_active', 'dish_count', 'created_time', 'updated_time']
        read_only_fields = ['id', 'created_time', 'updated_time']
    
    def get_dish_count(self, obj):
        """获取分类下菜品数量"""
        return obj.dishes.filter(is_active=True).count()


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """分类创建/更新序列化器"""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'image_url', 'sort_order', 'is_active']
    
    def validate_name(self, value):
        """验证分类名称"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError('分类名称至少2个字符')
        return value.strip()


class DishListSerializer(TimestampSerializer):
    """菜品列表序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    discount_rate = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    spicy_level_display = serializers.CharField(source='get_spicy_level_display', read_only=True)
    
    class Meta:
        model = Dish
        fields = [
            'id', 'category_id', 'category_name', 'name', 'description', 
            'price', 'original_price', 'discount_rate', 'image_url', 
            'stock_quantity', 'sales_count', 'is_recommended', 'is_active',
            'is_in_stock', 'tags', 'spicy_level', 'spicy_level_display',
            'created_time', 'updated_time'
        ]


class DishDetailSerializer(TimestampSerializer):
    """菜品详情序列化器"""
    category = CategorySerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    discount_rate = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    spicy_level_display = serializers.CharField(source='get_spicy_level_display', read_only=True)
    
    class Meta:
        model = Dish
        fields = [
            'id', 'category', 'category_name', 'name', 'description', 'price', 'original_price', 
            'discount_rate', 'image_url', 'image_urls', 'stock_quantity', 
            'sales_count', 'is_recommended', 'is_active', 'is_in_stock',
            'sort_order', 'tags', 'nutritional_info', 'spicy_level', 
            'spicy_level_display', 'created_time', 'updated_time'
        ]


class DishCreateUpdateSerializer(serializers.ModelSerializer):
    """菜品创建/更新序列化器"""
    
    class Meta:
        model = Dish
        fields = [
            'category', 'name', 'description', 'price', 'original_price',
            'image_url', 'image_urls', 'stock_quantity', 'is_recommended',
            'is_active', 'sort_order', 'tags', 'nutritional_info', 'spicy_level'
        ]
    
    def validate_name(self, value):
        """验证菜品名称"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError('菜品名称至少2个字符')
        return value.strip()
    
    def validate_price(self, value):
        """验证价格"""
        if value <= 0:
            raise serializers.ValidationError('价格必须大于0')
        return value
    
    def validate(self, attrs):
        """验证原价和现价关系"""
        price = attrs.get('price')
        original_price = attrs.get('original_price')
        
        if original_price and original_price < price:
            raise serializers.ValidationError('原价不能低于现价')
        
        return attrs


class DishSimpleSerializer(serializers.ModelSerializer):
    """菜品简单序列化器（用于订单等场景）"""
    
    class Meta:
        model = Dish
        fields = ['id', 'name', 'price', 'image_url']


class DishSearchSerializer(serializers.Serializer):
    """菜品搜索参数序列化器"""
    keyword = serializers.CharField(required=False, help_text='搜索关键词')
    category = serializers.IntegerField(required=False, help_text='分类ID')
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, help_text='最低价格')
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, help_text='最高价格')
    is_recommended = serializers.BooleanField(required=False, help_text='是否推荐')
    spicy_level = serializers.IntegerField(required=False, help_text='辣度等级')
    ordering = serializers.ChoiceField(
        choices=[
            'price', '-price', 'sales_count', '-sales_count', 
            'sort_order', '-sort_order', 'created_time', '-created_time'
        ],
        required=False,
        help_text='排序方式'
    ) 