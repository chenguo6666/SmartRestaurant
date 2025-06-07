from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.common.responses import APIResponse
from apps.common.pagination import StandardResultsSetPagination
from .models import Order
from .serializers import *
from .services import OrderService
import logging

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    """订单视图集"""
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payment_status']
    ordering_fields = ['created_time', 'final_amount']
    ordering = ['-created_time']
    
    def get_queryset(self):
        """动态查询集"""
        if hasattr(self.request.user, 'is_admin') and self.request.user.is_admin:
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
    
    def list(self, request, *args, **kwargs):
        """获取订单列表"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return APIResponse.success(serializer.data)
            
        except Exception as e:
            logger.error(f"获取订单列表失败: {str(e)}")
            return APIResponse.error("获取订单列表失败")
    
    def retrieve(self, request, *args, **kwargs):
        """获取订单详情"""
        try:
            order_service = OrderService()
            order = order_service.get_order_detail(kwargs['pk'], request.user)
            
            if not order:
                return APIResponse.not_found("订单不存在")
            
            # 权限检查
            if not (hasattr(request.user, 'is_admin') and request.user.is_admin) and order.user != request.user:
                return APIResponse.forbidden("只能查看自己的订单")
            
            serializer = self.get_serializer(order)
            return APIResponse.success(serializer.data)
            
        except Exception as e:
            logger.error(f"获取订单详情失败: {str(e)}")
            return APIResponse.error("获取订单详情失败")
    
    def create(self, request, *args, **kwargs):
        """创建订单"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                order_service = OrderService()
                order = order_service.create_order(request.user, serializer.validated_data)
                response_serializer = OrderDetailSerializer(order)
                return APIResponse.created(response_serializer.data, "订单创建成功")
            except ValueError as e:
                return APIResponse.error(str(e))
            except Exception as e:
                logger.error(f"创建订单失败: {str(e)}")
                return APIResponse.error("创建订单失败")
        return APIResponse.error("参数错误", serializer.errors)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消订单"""
        try:
            order = self.get_object()
            serializer = CancelOrderSerializer(data=request.data)
            
            if serializer.is_valid():
                order_service = OrderService()
                order = order_service.cancel_order(
                    order, 
                    request.user, 
                    serializer.validated_data.get('reason')
                )
                response_serializer = OrderDetailSerializer(order)
                return APIResponse.success(response_serializer.data, "订单已取消")
            
            return APIResponse.error("参数错误", serializer.errors)
            
        except (ValueError, PermissionError) as e:
            return APIResponse.error(str(e))
        except Exception as e:
            logger.error(f"取消订单失败: {str(e)}")
            return APIResponse.error("取消订单失败")
    
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """获取我的订单"""
        try:
            order_service = OrderService()
            
            # 获取查询参数
            status = request.query_params.get('status')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            
            result = order_service.get_user_orders(
                user=request.user,
                status=status,
                page=page,
                page_size=page_size
            )
            
            serializer = OrderListSerializer(result['orders'], many=True)
            
            return APIResponse.success({
                'orders': serializer.data,
                'pagination': {
                    'page': result['page'],
                    'page_size': result['page_size'],
                    'total': result['total'],
                    'total_pages': result['total_pages']
                }
            })
            
        except Exception as e:
            logger.error(f"获取我的订单失败: {str(e)}")
            return APIResponse.error("获取订单失败")
