from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Product, Specification, Category, Festival, Review
from utils.pricing import calculate_discounted_price
from datetime import timedelta

# -------------------------------
# Inline مشخصات محصول
# -------------------------------
class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1
    max_num = 10
    show_change_link = True


# -------------------------------
# Admin محصول
# -------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'price',
        'discount',
        'discount_duration_display',
        'time_left_display',
        'festival_discount_display',
        'discounted_price_display',
        'show_image',
        'slug'
    )
    list_filter = ('price', 'categories', 'discount')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('show_image', 'discounted_price_display', 'time_left_display')
    ordering = ('-id',)
    list_per_page = 20
    inlines = [SpecificationInline]
    filter_horizontal = ("categories",)

    fieldsets = (
        (None, {
            'fields': (
                'name', 'slug', 'price', 'description', 'image',
                'categories', 'discount', 'discount_start', 'discount_duration'
            )
        }),
    )

    # نمایش تصویر محصول
    def show_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" height="100" style="object-fit: cover;" />')
        return "تصویری ثبت نشده"
    show_image.short_description = 'پیش‌نمایش تصویر'

    # نمایش تخفیف جشنواره
    def festival_discount_display(self, obj):
        active_festivals = Festival.objects.filter(
            active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )
        if active_festivals.exists():
            festival = active_festivals.latest("start_date")
            return f"{festival.discount_percentage}%"
        return "-"
    festival_discount_display.short_description = "تخفیف جشنواره"

    # نمایش قیمت نهایی
    def discounted_price_display(self, obj):
        price = calculate_discounted_price(obj)
        return f"{price:,.0f} تومان"
    discounted_price_display.short_description = "قیمت نهایی"

    # نمایش مدت زمان تخفیف محصول
    def discount_duration_display(self, obj):
        if obj.discount_duration:
            return f"{obj.discount_duration} ساعت"
        return "-"
    discount_duration_display.short_description = "مدت تخفیف"

    # نمایش زمان باقی‌مانده تخفیف
    def time_left_display(self, obj):
        if obj.discount and obj.discount_start and obj.discount_duration:
            end_time = obj.discount_start + timedelta(hours=obj.discount_duration)
            remaining = end_time - timezone.now()
            if remaining.total_seconds() > 0:
                hours = remaining.total_seconds() // 3600
                minutes = (remaining.total_seconds() % 3600) // 60
                return f"{int(hours)} ساعت و {int(minutes)} دقیقه باقی مانده"
        return "-"
    time_left_display.short_description = "زمان باقی‌مانده تخفیف"


# -------------------------------
# Admin مشخصات محصول
# -------------------------------
@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'value', 'product')
    list_filter = ('product',)
    search_fields = ('title', 'value')
    ordering = ('-id',)


# -------------------------------
# Admin دسته‌بندی
# -------------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("parent",)


# -------------------------------
# Admin جشنواره‌ها
# -------------------------------
@admin.register(Festival)
class FestivalAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'discount_percentage', 'start_date', 'end_date', 'active')
    list_filter = ('active',)
    search_fields = ('name',)
    ordering = ('-start_date',)



@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("text", "user__username", "product__name")
    ordering = ("-created_at",)