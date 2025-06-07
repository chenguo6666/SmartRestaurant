from django.urls import path
from . import views

app_name = 'dishes'

urlpatterns = [
    # 分类相关API
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:id>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # 菜品相关API
    path('dishes/', views.DishListView.as_view(), name='dish-list'),
    path('dishes/<int:id>/', views.DishDetailView.as_view(), name='dish-detail'),
    path('dishes/search/', views.dish_search, name='dish-search'),
    path('dishes/recommended/', views.recommended_dishes, name='recommended-dishes'),
    path('dishes/hot/', views.hot_dishes, name='hot-dishes'),
    
    # 管理员API（可选）
    path('admin/categories/', views.CategoryCreateView.as_view(), name='admin-category-create'),
    path('admin/dishes/', views.DishCreateView.as_view(), name='admin-dish-create'),
] 