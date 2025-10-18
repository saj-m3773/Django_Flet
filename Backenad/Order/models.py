from django.db import models
from django.conf import settings
from products.models import Product  # فرض می‌کنم محصول اینجاست


User = settings.AUTH_USER_MODEL

class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  # فقط یک سبد فعال داریم

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"سبد خرید {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار پرداخت"),
        ("paid", "پرداخت شده"),
        ("failed", "پرداخت ناموفق"),
        ("canceled", "لغو شده"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    cart = models.OneToOneField(   # هر سفارش یک سبد خرید دارد
        Cart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order"
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    authority = models.CharField(max_length=255, blank=True, null=True)  # کد تراکنش درگاه

    def __str__(self):
        return f"Order #{self.id} - {self.user} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=0)  # قیمت در لحظه خرید

    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

# پرداخت
class Payment(models.Model):
    STATUS_CHOICES = [
        ("init", "در حال انتظار"),
        ("success", "موفق"),
        ("failed", "ناموفق"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="init")
    authority = models.CharField(max_length=255, blank=True, null=True)  # کد شاپرک
    ref_id = models.CharField(max_length=255, blank=True, null=True)  # کد پیگیری بانک
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return f"پرداخت {self.id} - سفارش {self.order.id} - {self.status}"