# 智慧餐厅系统 - API接口设计与实现

## 1. API设计规范

### 1.1 RESTful API规范
- 使用HTTP动词：GET(查询)、POST(创建)、PUT(完整更新)、PATCH(部分更新)、DELETE(删除)
- URL命名：使用复数形式，层级清晰
- 统一的响应格式
- 合理的HTTP状态码

### 1.2 URL设计规范
```
# 资源集合
GET /api/dishes/           # 获取菜品列表
POST /api/dishes/          # 创建菜品

# 单个资源
GET /api/dishes/{id}/      # 获取单个菜品
PUT /api/dishes/{id}/      # 完整更新菜品
PATCH /api/dishes/{id}/    # 部分更新菜品
DELETE /api/dishes/{id}/   # 删除菜品

# 嵌套资源
GET /api/orders/{id}/items/     # 获取订单项
POST /api/orders/{id}/cancel/   # 取消订单

# 管理员接口前缀
GET /api/admin/dishes/     # 管理员菜品接口
```

### 1.3 统一响应格式
```json
{
    "code": 200,
    "message": "操作成功",
    "data": {
        // 响应数据
    },
    "errors": null
}
```

## 2. Django REST Framework配置

### 2.1 序列化器基类
**apps/common/serializers.py**：
```python
from rest_framework import serializers
from rest_framework.fields import empty

class BaseSerializer(serializers.ModelSerializer):
    """序列化器基类"""
    
    def __init__(self, instance=None, data=empty, **kwargs):
        # 动态字段选择
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)
        
        super().__init__(instance, data, **kwargs)
        
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        
        if exclude is not None:
            for field_name in exclude:
                self.fields.pop(field_name, None)

class TimestampSerializer(serializers.ModelSerializer):
    """时间戳序列化器"""
    created_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    updated_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    
    class Meta:
        abstract = True
```

### 2.2 分页配置
**apps/common/pagination.py**：
```python
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardResultsSetPagination(PageNumberPagination):
    """标准分页类"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'results': data,
                'pagination': {
                    'count': self.page.paginator.count,
                    'current_page': self.page.number,
                    'total_pages': self.page.paginator.num_pages,
                    'page_size': self.get_page_size(self.request),
                    'has_next': self.page.has_next(),
                    'has_previous': self.page.has_previous(),
                }
            }
        })

class LargeResultsSetPagination(PageNumberPagination):
    """大数据集分页"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
```

### 2.3 统一响应处理
**apps/common/responses.py**：
```python
from rest_framework.response import Response
from rest_framework import status

class APIResponse:
    """统一API响应类"""
    
    @staticmethod
    def success(data=None, message="操作成功", code=200, status_code=status.HTTP_200_OK):
        return Response({
            'code': code,
            'message': message,
            'data': data,
            'errors': None
        }, status=status_code)
    
    @staticmethod
    def error(message="操作失败", errors=None, code=400, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            'code': code,
            'message': message,
            'data': None,
            'errors': errors
        }, status=status_code)
    
    @staticmethod
    def created(data=None, message="创建成功"):
        return APIResponse.success(data, message, 201, status.HTTP_201_CREATED)
    
    @staticmethod
    def no_content(message="删除成功"):
        return APIResponse.success(None, message, 204, status.HTTP_204_NO_CONTENT)
    
    @staticmethod
    def unauthorized(message="未授权访问"):
        return APIResponse.error(message, None, 401, status.HTTP_401_UNAUTHORIZED)
    
    @staticmethod
    def forbidden(message="权限不足"):
        return APIResponse.error(message, None, 403, status.HTTP_403_FORBIDDEN)
    
    @staticmethod
    def not_found(message="资源不存在"):
        return APIResponse.error(message, None, 404, status.HTTP_404_NOT_FOUND)
```

## 3. 菜品相关API

### 3.1 菜品序列化器
**apps/dishes/serializers.py**：
```python
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
    display_price = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Dish
        fields = [
            'id', 'name', 'description', 'price', 'original_price', 
            'display_price', 'image_url', 'category_name', 'sales_count',
            'is_recommended', 'is_active', 'spicy_level', 'tags',
            'is_in_stock', 'created_time'
        ]
    
    def get_display_price(self, obj):
        return obj.get_display_price()
    
    def get_is_in_stock(self, obj):
        return obj.is_in_stock()

class DishDetailSerializer(DishListSerializer):
    """菜品详情序列化器"""
    category = CategorySerializer(read_only=True)
    image_urls = serializers.JSONField()
    nutritional_info = serializers.JSONField()
    avg_rating = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)
    
    class Meta(DishListSerializer.Meta):
        fields = DishListSerializer.Meta.fields + [
            'category', 'image_urls', 'stock_quantity', 'sort_order',
            'nutritional_info', 'avg_rating', 'total_reviews', 'updated_time'
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
    
    def validate_price(self, value):
        """验证价格"""
        if value <= 0:
            raise serializers.ValidationError('价格必须大于0')
        return value
    
    def validate_name(self, value):
        """验证菜品名称"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError('菜品名称至少2个字符')
        return value.strip()
    
    def validate(self, attrs):
        """交叉验证"""
        price = attrs.get('price')
        original_price = attrs.get('original_price')
        
        if original_price and original_price <= price:
            raise serializers.ValidationError('原价必须大于现价')
        
        return attrs
```

### 3.2 菜品视图集
**apps/dishes/views.py**：
```python
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.common.permissions import IsAdminUser, IsActiveUser
from apps.common.responses import APIResponse
from apps.common.pagination import StandardResultsSetPagination
from .models import Category, Dish
from .serializers import *
from .services import DishService, CategoryService
from .filters import DishFilter

class CategoryViewSet(viewsets.ModelViewSet):
    """分类视图集"""
    queryset = Category.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['sort_order', 'created_time']
    ordering = ['-sort_order', 'id']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateUpdateSerializer
        return CategorySerializer
    
    def get_permissions(self):
        """动态权限"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsActiveUser]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        """获取分类列表"""
        # 只返回启用的分类
        queryset = self.get_queryset().filter(is_active=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建分类"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            category_service = CategoryService()
            category = category_service.create_category(
                serializer.validated_data, 
                request.user
            )
            response_serializer = CategorySerializer(category)
            return APIResponse.created(response_serializer.data)
        return APIResponse.error("参数错误", serializer.errors)
    
    @action(detail=True, methods=['get'])
    def dishes(self, request, pk=None):
        """获取分类下的菜品"""
        category = self.get_object()
        dishes = category.dishes.filter(is_active=True).order_by('-sort_order', '-sales_count')
        
        page = self.paginate_queryset(dishes)
        if page is not None:
            serializer = DishListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = DishListSerializer(dishes, many=True)
        return APIResponse.success(serializer.data)

class DishViewSet(viewsets.ModelViewSet):
    """菜品视图集"""
    queryset = Dish.objects.select_related('category').all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DishFilter
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['price', 'sales_count', 'sort_order', 'created_time']
    ordering = ['-sort_order', '-sales_count']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DishListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return DishCreateUpdateSerializer
        return DishDetailSerializer
    
    def get_permissions(self):
        """动态权限"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsActiveUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """动态查询集"""
        if self.action in ['list', 'retrieve'] and not self.request.user.is_admin:
            # 普通用户只能看到上架的菜品
            return self.queryset.filter(is_active=True)
        return self.queryset
    
    def list(self, request, *args, **kwargs):
        """获取菜品列表"""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """获取菜品详情"""
        dish_service = DishService()
        dish_data = dish_service.get_dish_detail(kwargs['pk'])
        
        if not dish_data:
            return APIResponse.not_found("菜品不存在")
        
        # 手动构造序列化数据
        serializer = self.get_serializer(dish_data['dish'])
        data = serializer.data
        data['avg_rating'] = dish_data['avg_rating']
        data['total_reviews'] = dish_data['total_reviews']
        
        return APIResponse.success(data)
    
    def create(self, request, *args, **kwargs):
        """创建菜品"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            dish_service = DishService()
            dish = dish_service.create_dish(
                serializer.validated_data,
                request.user
            )
            response_serializer = DishDetailSerializer(dish)
            return APIResponse.created(response_serializer.data)
        return APIResponse.error("参数错误", serializer.errors)
    
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """获取推荐菜品"""
        dish_service = DishService()
        dishes = dish_service.get_recommended_dishes()
        serializer = DishListSerializer(dishes, many=True)
        return APIResponse.success(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories_with_dishes(self, request):
        """获取分类及其菜品"""
        dish_service = DishService()
        data = dish_service.get_categories_with_dishes()
        
        result = []
        for item in data:
            category_data = CategorySerializer(item['category']).data
            dishes_data = DishListSerializer(item['dishes'], many=True).data
            result.append({
                'category': category_data,
                'dishes': dishes_data
            })
        
        return APIResponse.success(result)
```

### 3.3 菜品过滤器
**apps/dishes/filters.py**：
```python
import django_filters
from .models import Dish

class DishFilter(django_filters.FilterSet):
    """菜品过滤器"""
    category = django_filters.NumberFilter(field_name='category_id')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    is_recommended = django_filters.BooleanFilter()
    spicy_level = django_filters.NumberFilter()
    
    class Meta:
        model = Dish
        fields = ['category', 'min_price', 'max_price', 'is_recommended', 'spicy_level']
```

## 4. 订单相关API

### 4.1 订单序列化器
**apps/orders/serializers.py**：
```python
from rest_framework import serializers
from apps.common.serializers import TimestampSerializer
from apps.dishes.serializers import DishListSerializer
from apps.users.serializers import UserSerializer
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    """订单项序列化器"""
    dish = DishListSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'dish', 'dish_name', 'dish_price', 'dish_image_url',
            'quantity', 'subtotal', 'special_requests'
        ]

class OrderListSerializer(TimestampSerializer):
    """订单列表序列化器"""
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_no', 'user_nickname', 'total_amount', 
            'discount_amount', 'final_amount', 'status', 'status_display',
            'payment_status', 'table_number', 'item_count', 'created_time'
        ]
    
    def get_item_count(self, obj):
        """获取订单项数量"""
        return obj.items.count()

class OrderDetailSerializer(OrderListSerializer):
    """订单详情序列化器"""
    user = UserSerializer(read_only=True, fields=['id', 'nickname', 'phone'])
    items = OrderItemSerializer(many=True, read_only=True)
    coupon_name = serializers.CharField(source='coupon.name', read_only=True)
    
    class Meta(OrderListSerializer.Meta):
        fields = OrderListSerializer.Meta.fields + [
            'user', 'items', 'customer_notes', 'admin_notes',
            'estimated_time', 'coupon_name', 'paid_time', 
            'completed_time', 'cancelled_time', 'updated_time'
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
        
        return value

class UpdateOrderStatusSerializer(serializers.Serializer):
    """更新订单状态序列化器"""
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)

class CancelOrderSerializer(serializers.Serializer):
    """取消订单序列化器"""
    reason = serializers.CharField(max_length=200, required=False, allow_blank=True)
```

### 4.2 订单视图集
**apps/orders/views.py**：
```python
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.common.permissions import IsAdminUser, IsActiveUser, IsOwnerOrAdmin
from apps.common.responses import APIResponse
from apps.common.pagination import StandardResultsSetPagination
from .models import Order
from .serializers import *
from .services import OrderService
from .filters import OrderFilter

class OrderViewSet(viewsets.ModelViewSet):
    """订单视图集"""
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ['created_time', 'final_amount']
    ordering = ['-created_time']
    
    def get_queryset(self):
        """动态查询集"""
        if self.request.user.is_admin:
            return Order.objects.select_related('user', 'coupon').prefetch_related('items__dish')
        else:
            return Order.objects.filter(user=self.request.user).select_related('coupon').prefetch_related('items__dish')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return CreateOrderSerializer
        elif self.action == 'update_status':
            return UpdateOrderStatusSerializer
        elif self.action == 'cancel':
            return CancelOrderSerializer
        return OrderDetailSerializer
    
    def get_permissions(self):
        """动态权限"""
        if self.action in ['update_status'] or (self.action in ['list', 'retrieve'] and self.request.user.is_admin):
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsActiveUser]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        """获取订单列表"""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """获取订单详情"""
        order_service = OrderService()
        order = order_service.get_order_detail(kwargs['pk'], request.user)
        
        if not order:
            return APIResponse.not_found("订单不存在")
        
        # 权限检查
        if not request.user.is_admin and order.user != request.user:
            return APIResponse.forbidden("只能查看自己的订单")
        
        serializer = self.get_serializer(order)
        return APIResponse.success(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建订单"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                order_service = OrderService()
                order = order_service.create_order(request.user, serializer.validated_data)
                response_serializer = OrderDetailSerializer(order)
                return APIResponse.created(response_serializer.data)
            except ValueError as e:
                return APIResponse.error(str(e))
        return APIResponse.error("参数错误", serializer.errors)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消订单"""
        order = self.get_object()
        serializer = CancelOrderSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                order_service = OrderService()
                order = order_service.cancel_order(
                    order, 
                    request.user, 
                    serializer.validated_data.get('reason')
                )
                response_serializer = OrderDetailSerializer(order)
                return APIResponse.success(response_serializer.data, "订单已取消")
            except (ValueError, PermissionError) as e:
                return APIResponse.error(str(e))
        return APIResponse.error("参数错误", serializer.errors)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """更新订单状态（管理员）"""
        order = self.get_object()
        serializer = UpdateOrderStatusSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                order_service = OrderService()
                order = order_service.update_order_status(
                    order,
                    serializer.validated_data['status'],
                    request.user,
                    serializer.validated_data.get('notes')
                )
                response_serializer = OrderDetailSerializer(order)
                return APIResponse.success(response_serializer.data, "状态更新成功")
            except ValueError as e:
                return APIResponse.error(str(e))
        return APIResponse.error("参数错误", serializer.errors)
    
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """获取我的订单"""
        order_service = OrderService()
        status_filter = request.query_params.get('status')
        page = int(request.query_params.get('page', 1))
        
        result = order_service.get_user_orders(
            request.user, 
            status_filter, 
            page
        )
        
        serializer = OrderListSerializer(result['orders'], many=True)
        return APIResponse.success({
            'orders': serializer.data,
            'pagination': {
                'current_page': result['page'],
                'total_pages': result['total_pages'],
                'total': result['total'],
                'page_size': result['page_size']
            }
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def statistics(self, request):
        """订单统计（管理员）"""
        order_service = OrderService()
        
        # 解析日期范围
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        date_range = None
        if start_date and end_date:
            from datetime import datetime
            date_range = (
                datetime.strptime(start_date, '%Y-%m-%d').date(),
                datetime.strptime(end_date, '%Y-%m-%d').date()
            )
        
        stats = order_service.get_order_statistics(date_range)
        return APIResponse.success(stats)
```

## 5. URL路由配置

### 5.1 主路由配置
**smart_restaurant/urls.py**：
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API路由
    path('api/', include([
        path('users/', include('apps.users.urls')),
        path('dishes/', include('apps.dishes.urls')),
        path('categories/', include('apps.dishes.category_urls')),
        path('orders/', include('apps.orders.urls')),
        path('payments/', include('apps.payments.urls')),
        path('coupons/', include('apps.coupons.urls')),
        path('reviews/', include('apps.reviews.urls')),
        path('restaurant/', include('apps.restaurant.urls')),
    ])),
    
    # API文档
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # 健康检查
    path('health/', lambda request: JsonResponse({'status': 'ok'})),
]

# 开发环境静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### 5.2 应用路由配置
**apps/dishes/urls.py**：
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.DishViewSet, basename='dishes')

app_name = 'dishes'
urlpatterns = [
    path('', include(router.urls)),
]
```

**apps/dishes/category_urls.py**：
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet

router = DefaultRouter()
router.register('', CategoryViewSet, basename='categories')

urlpatterns = [
    path('', include(router.urls)),
]
```

## 6. API测试用例

### 6.1 菜品API测试
```bash
# 获取菜品列表
curl -X GET "http://localhost:8000/api/dishes/" \
  -H "Authorization: Bearer your-token"

# 搜索菜品
curl -X GET "http://localhost:8000/api/dishes/?search=宫保鸡丁&category=1&min_price=10&max_price=50" \
  -H "Authorization: Bearer your-token"

# 获取菜品详情
curl -X GET "http://localhost:8000/api/dishes/1/" \
  -H "Authorization: Bearer your-token"

# 获取推荐菜品
curl -X GET "http://localhost:8000/api/dishes/recommended/" \
  -H "Authorization: Bearer your-token"

# 创建菜品（管理员）
curl -X POST "http://localhost:8000/api/dishes/" \
  -H "Authorization: Bearer admin-token" \
  -H "Content-Type: application/json" \
  -d '{
    "category": 1,
    "name": "红烧肉",
    "description": "经典红烧肉",
    "price": 28.00,
    "image_url": "https://example.com/image.jpg",
    "stock_quantity": 50,
    "is_recommended": true
  }'
```

### 6.2 订单API测试
```bash
# 创建订单
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "cart_items": [
      {
        "dish_id": 1,
        "quantity": 2,
        "special_requests": "不要辣"
      },
      {
        "dish_id": 2,
        "quantity": 1
      }
    ],
    "table_number": "A01",
    "customer_notes": "快点上菜",
    "coupon_code": "DISCOUNT10"
  }'

# 获取我的订单
curl -X GET "http://localhost:8000/api/orders/my_orders/?status=pending_payment" \
  -H "Authorization: Bearer your-token"

# 取消订单
curl -X POST "http://localhost:8000/api/orders/1/cancel/" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "不想要了"
  }'

# 更新订单状态（管理员）
curl -X PATCH "http://localhost:8000/api/orders/1/update_status/" \
  -H "Authorization: Bearer admin-token" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "preparing",
    "notes": "开始制作"
  }'
```

## 7. API文档自动生成

### 7.1 drf-spectacular配置
**settings.py中添加**：
```python
SPECTACULAR_SETTINGS = {
    'TITLE': '智慧餐厅API文档',
    'DESCRIPTION': '智慧餐厅点餐系统的API接口文档',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
}
```

### 7.2 Swagger注解示例
```python
from drf_spectacular.utils import extend_schema, OpenApiParameter

class DishViewSet(viewsets.ModelViewSet):
    @extend_schema(
        summary="获取菜品列表",
        description="获取所有启用的菜品列表，支持分类过滤、价格筛选、关键词搜索",
        parameters=[
            OpenApiParameter(name='category', description='分类ID', required=False, type=int),
            OpenApiParameter(name='search', description='搜索关键词', required=False, type=str),
            OpenApiParameter(name='min_price', description='最低价格', required=False, type=float),
            OpenApiParameter(name='max_price', description='最高价格', required=False, type=float),
        ],
        responses={200: DishListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        # 实现代码...
        pass
```

API接口设计确保了前后端的高效对接，提供了完整的RESTful接口和详细的文档支持。 