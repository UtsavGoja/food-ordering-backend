from rest_framework.generics import CreateAPIView
from .serializers import *
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, viewsets,status
from rest_framework.response import Response


class RegisterView(CreateAPIView):
    serializer_class=RegisterSerializer
    

class CategoryViewset(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class=CategorySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
class MenuItemViewset(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class=MenuItemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name']
    
    def get_permissions(self):
            if self.action in ['list', 'retrieve']:
                return [AllowAny()]
            return [IsAdminUser()]
        
        
        
class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # only ever show items from the logged-in user's own cart
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        menu_item = serializer.validated_data['menu_item']
        quantity = serializer.validated_data.get('quantity', 1)

        item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        serializer.instance = item
        
        
        
class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.item.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        delivery_address = request.data.get('delivery_address')
        if not delivery_address:
            return Response({"error": "delivery_address is required"}, status=status.HTTP_400_BAD_REQUEST)

        total = sum(item.menu_item.price * item.quantity for item in cart.item.all())
        order = Order.objects.create(user=request.user, delivery_address=delivery_address, total_price=total)

        for item in cart.item.all():
            OrderItem.objects.create(
                order=order,
                menu_item=item.menu_item,
                quantity=item.quantity,
                price_at_purchase=item.menu_item.price
            )

        cart.item.all().delete()  # clear cart after order placed

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
    
class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    lookup_url_kwarg = 'order_id'

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get('status')

        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)