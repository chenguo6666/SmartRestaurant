from django.shortcuts import render
from django.db.models import Q
from rest_framework import generics, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.common.responses import APIResponse
from apps.common.pagination import StandardResultsSetPagination
from .models import Category, Dish
from .serializers import (
    CategorySerializer, CategoryCreateUpdateSerializer,
    DishListSerializer, DishDetailSerializer, DishCreateUpdateSerializer
)


class CategoryListView(generics.ListAPIView):
    """分类列表视图"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data, message="获取分类列表成功")


class CategoryDetailView(generics.RetrieveAPIView):
    """分类详情视图"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return APIResponse.success(data=serializer.data, message="获取分类详情成功")
        except Category.DoesNotExist:
            return APIResponse.not_found(message="分类不存在")


class DishListView(generics.ListAPIView):
    """菜品列表视图"""
    queryset = Dish.objects.filter(is_active=True).select_related('category')
    serializer_class = DishListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_recommended', 'spicy_level']
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['price', 'sales_count', 'sort_order', 'created_time']
    ordering = ['-sort_order', '-sales_count']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 处理category参数，确保不处理无效的category值
        category_id = self.request.query_params.get('category')
        if category_id and category_id != 'null' and category_id != 'undefined':
            try:
                category_id = int(category_id)
                queryset = queryset.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass  # 忽略无效的category参数
        
        # 价格范围筛选
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            try:
                min_price = float(min_price)
                queryset = queryset.filter(price__gte=min_price)
            except ValueError:
                pass
        
        if max_price:
            try:
                max_price = float(max_price)
                queryset = queryset.filter(price__lte=max_price)
            except ValueError:
                pass
        
        # 关键词搜索（支持菜品名称和描述）
        keyword = self.request.query_params.get('search')
        if keyword and keyword.strip():
            queryset = queryset.filter(
                Q(name__icontains=keyword) | 
                Q(description__icontains=keyword) |
                Q(tags__icontains=keyword)
            )
        
        return queryset


class DishDetailView(generics.RetrieveAPIView):
    """菜品详情视图"""
    queryset = Dish.objects.filter(is_active=True).select_related('category')
    serializer_class = DishDetailSerializer
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return APIResponse.success(data=serializer.data, message="获取菜品详情成功")
        except Dish.DoesNotExist:
            return APIResponse.not_found(message="菜品不存在")


@api_view(['GET'])
def dish_search(request):
    """菜品搜索API"""
    # 支持多种参数名：q, keyword, search
    keyword = (
        request.GET.get('q', '') or 
        request.GET.get('keyword', '') or 
        request.GET.get('search', '')
    ).strip()
    
    if not keyword:
        return APIResponse.error(message="请输入搜索关键词")
    
    # 搜索菜品名称、描述和标签
    dishes = Dish.objects.filter(
        Q(name__icontains=keyword) | 
        Q(description__icontains=keyword) |
        Q(tags__icontains=keyword),
        is_active=True
    ).select_related('category')[:20]  # 限制返回20条结果
    
    serializer = DishListSerializer(dishes, many=True)
    
    return APIResponse.success(
        data=serializer.data, 
        message=f"搜索到 {len(dishes)} 个结果"
    )


@api_view(['GET'])
def recommended_dishes(request):
    """推荐菜品API"""
    dishes = Dish.objects.filter(
        is_recommended=True, 
        is_active=True
    ).select_related('category').order_by('-sort_order', '-sales_count')[:10]
    
    serializer = DishListSerializer(dishes, many=True)
    
    return APIResponse.success(
        data=serializer.data,
        message="获取推荐菜品成功"
    )


@api_view(['GET'])
def hot_dishes(request):
    """热销菜品API"""
    dishes = Dish.objects.filter(
        is_active=True
    ).select_related('category').order_by('-sales_count')[:10]
    
    serializer = DishListSerializer(dishes, many=True)
    
    return APIResponse.success(
        data=serializer.data,
        message="获取热销菜品成功"
    )


# 管理员用的CRUD视图（后续如果需要管理功能）
class CategoryCreateView(generics.CreateAPIView):
    """创建分类（管理员）"""
    queryset = Category.objects.all()
    serializer_class = CategoryCreateUpdateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.created(data=serializer.data, message="分类创建成功")
        return APIResponse.error(message="参数错误", errors=serializer.errors)


class DishCreateView(generics.CreateAPIView):
    """创建菜品（管理员）"""
    queryset = Dish.objects.all()
    serializer_class = DishCreateUpdateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.created(data=serializer.data, message="菜品创建成功")
        return APIResponse.error(message="参数错误", errors=serializer.errors)
