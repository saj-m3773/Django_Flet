import requests
from rest_framework import viewsets, status, generics, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from Backenad import settings
from .models import Cart, CartItem, Order, OrderItem, Payment
from .serializers import CartSerializer, OrderSerializer, PaymentSerializer


# -------------------------------- سبد خرید --------------------------------
class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def add_item(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
        if not created:
            item.quantity += quantity
        item.save()

        return Response({"message": "محصول به سبد خرید اضافه شد"}, status=status.HTTP_200_OK)

    def remove_item(self, request, pk=None):
        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
        try:
            item = cart.items.get(id=pk)
            item.delete()
            return Response({"message": "محصول حذف شد"})
        except CartItem.DoesNotExist:
            return Response({"error": "محصول یافت نشد"}, status=status.HTTP_404_NOT_FOUND)


class CartItemDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CartItem.objects.all()

    def delete(self, request, *args, **kwargs):
        item_id = kwargs.get("pk")
        try:
            cart_item = CartItem.objects.get(pk=item_id, cart__user=request.user)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"error": "آیتم پیدا نشد"}, status=status.HTTP_404_NOT_FOUND)


class CartItemUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CartItem.objects.all()
    http_method_names = ["patch"]

    def patch(self, request, *args, **kwargs):
        item_id = kwargs.get("pk")
        quantity = request.data.get("quantity")

        if quantity is None:
            return Response({"error": "quantity مورد نیاز است"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.get(pk=item_id, cart__user=request.user)
            cart_item.quantity = int(quantity)
            cart_item.save()
            return Response({"id": cart_item.id, "quantity": cart_item.quantity}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({"error": "آیتم پیدا نشد"}, status=status.HTTP_404_NOT_FOUND)


# -------------------------------- سفارش --------------------------------
class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def create(self, request):
        cart = get_object_or_404(Cart, user=request.user, is_active=True)

        if not cart.items.exists():
            return Response({"error": "سبد خرید خالی است"}, status=status.HTTP_400_BAD_REQUEST)

        # محاسبه مجموع قیمت
        total_price = sum(item.product.price * item.quantity for item in cart.items.all())

        # ایجاد سفارش
        order = Order.objects.create(user=request.user, total_price=total_price)

        # کپی آیتم‌ها به سفارش
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart.is_active = False
        cart.save()

        return Response(
            {"order_id": order.id, "total_price": total_price},
            status=status.HTTP_201_CREATED
        )


# -------------------------------- پرداخت --------------------------------
class PaymentRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "سفارش یافت نشد"}, status=status.HTTP_404_NOT_FOUND)

        payment, created = Payment.objects.get_or_create(
            order=order,
            user=request.user,
            defaults={"amount": order.total_price}
        )

        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": order.total_price,
            "description": f"پرداخت سفارش {order.id}",
            "callback_url": "http://127.0.0.1:8550/payment-result",
        }

        zarin_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
        response = requests.post(zarin_url, json=data)
        res_data = response.json()

        if res_data.get("Status") == 100:
            payment.authority = res_data.get("Authority")
            payment.save()
            return Response({"authority": payment.authority}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "خطا در ارتباط با درگاه"}, status=status.HTTP_400_BAD_REQUEST)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        authority = request.data.get("authority")
        status_str = request.data.get("status")
        order_id = request.data.get("order_id")

        if not authority or not order_id:
            return Response({"error": "اطلاعات ناقص"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
            payment = Payment.objects.get(order=order)
        except (Order.DoesNotExist, Payment.DoesNotExist):
            return Response({"error": "سفارش یا پرداخت یافت نشد"}, status=status.HTTP_404_NOT_FOUND)

        if status_str != "OK":
            payment.status = "failed"
            payment.save()
            return Response({"status": "failed"}, status=status.HTTP_200_OK)

        verify_data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": payment.amount,
            "authority": authority,
        }

        verify_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
        response = requests.post(verify_url, json=verify_data)
        res_data = response.json()

        if res_data.get("Status") == 100:
            payment.status = "success"
            payment.ref_id = res_data.get("RefID")
            payment.save()
            order.is_paid = True
            order.save()
            return Response(
                {"status": "success", "ref_id": payment.ref_id},
                status=status.HTTP_200_OK
            )
        else:
            payment.status = "failed"
            payment.save()
            return Response({"status": "failed"}, status=status.HTTP_200_OK)
