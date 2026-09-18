from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('categories',  CategoryViewset)
router.register('menu-items',  MenuItemViewset)
router.register('cart-items', CartItemViewSet, basename='cart-item')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:order_id>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('', include(router.urls))
]   