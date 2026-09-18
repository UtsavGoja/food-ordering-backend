from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone_number', 'address']
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email',''),
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number',''),
            address=validated_data.get('address','')
        )
        return user
    
    
class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ['id', 'name']
    
    
class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset = Category.objects.all(),
        source = 'category',
        write_only = True
    )
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'category', 'category_id', 'price', 'is_available']
        
class CartItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset = MenuItem.objects.all(), source = "menu_item", write_only = True
    )
    
    class Meta:
        model = CartItem
        fields = ["id", "quantity", "menu_item", "menu_item_id"]
        
        
class CartSerializer(serializers.ModelSerializer):
    item = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'item']
        
        
class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'quantity', 'price_at_purchase']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'delivery_address', 'total_price', 'created_at', 'items']
        read_only_fields = ['status', 'total_price']