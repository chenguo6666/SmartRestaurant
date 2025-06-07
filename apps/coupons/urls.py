from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet

app_name = 'coupons'

router = DefaultRouter()
router.register(r'', CouponViewSet, basename='coupons')

urlpatterns = [
    path('', include(router.urls)),
] 