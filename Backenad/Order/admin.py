from django.contrib import admin
from .models import Cart, CartItem, Order, Payment


# ---------------- Cart ----------------
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("total_price_display",)

    def total_price_display(self, obj):
        return obj.total_price()
    total_price_display.short_description = "قیمت کل آیتم"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_active", "created_at", "updated_at", "total_price_display")
    list_filter = ("is_active", "created_at")
    search_fields = ("user__username",)
    inlines = [CartItemInline]

    def total_price_display(self, obj):
        return obj.total_price()
    total_price_display.short_description = "مجموع کل سبد"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity", "total_price_display")
    search_fields = ("product__name", "cart__user__username")

    def total_price_display(self, obj):
        return obj.total_price()
    total_price_display.short_description = "قیمت کل آیتم"


# ---------------- Orders ----------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price_display", "created_at")
    list_filter = ("status", "created_at")

    readonly_fields = ("total_price_display",)

    def total_price_display(self, obj):
        return obj.total_price()
    total_price_display.short_description = "مجموع کل سفارش"


# ---------------- Payments ----------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "amount", "status", "authority", "ref_id", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ( "authority", "ref_id")
    readonly_fields = ("amount", "authority", "ref_id")
    #order__id", "order__user__username"
