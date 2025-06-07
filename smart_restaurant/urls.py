"""
URL configuration for smart_restaurant project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def api_status(request):
    """API状态检查视图"""
    return JsonResponse({
        'status': 'ok',
        'message': '智能餐厅系统API运行正常',
        'version': '1.0.0'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_status, name='api_status'),  # 根路径显示API状态
    path('api/', include('apps.dishes.urls')),  # 菜品API路由
    path('api/orders/', include('apps.orders.urls')),  # 订单API路由
    path('api/coupons/', include('apps.coupons.urls')),  # 优惠券API路由
]

# 开发环境静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug Toolbar配置
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        urlpatterns = [
            path('__debug__/', include('debug_toolbar.urls')),
        ] + urlpatterns
