from django.urls import path
from .views import (
    CartViewSet, CartItemDeleteView, CartItemUpdateView,
    OrderViewSet, PaymentRequestView, VerifyPaymentView
)

# ---- Cart ----
cart_list = CartViewSet.as_view({
    'get': 'list',
    'post': 'add_item'
})
cart_remove = CartViewSet.as_view({
    'delete': 'remove_item'
})

# ---- Orders ----
order_list = OrderViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

urlpatterns = [
    # ----------------- Cart -----------------
    path("cart/", cart_list, name="cart"),
    path("cart/item/<int:pk>/remove/", cart_remove, name="remove-item"),
    path("cart/item/<int:pk>/delete/", CartItemDeleteView.as_view(), name="cart-item-delete"),
    path("cart/item/<int:pk>/update/", CartItemUpdateView.as_view(), name="cart-item-update"),

    # ----------------- Orders -----------------
    path("orders/", order_list, name="order-list-create"),

    # ----------------- Payments -----------------
    # درخواست پرداخت (ارسال به درگاه)
    path("orders/<int:order_id>/payment/", PaymentRequestView.as_view(), name="payment-create"),

    # تأیید پرداخت (بازگشت از درگاه)
    path("payment/verify/", VerifyPaymentView.as_view(), name="payment-verify"),
]
