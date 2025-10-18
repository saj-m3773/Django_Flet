
from rest_framework import serializers
from .models import Cart, CartItem, Payment, OrderItem, Order
from products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]

    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        return obj.total_price()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]

    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        return obj.total_price()

# ================= سفارش =================
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "total_price"]

    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        return obj.total_price()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "items", "status", "total_price", "created_at"]

    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        return obj.total_price()


# ================= پرداخت =================
class PaymentSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "order", "amount", "status", "authority", "ref_id", "created_at"]