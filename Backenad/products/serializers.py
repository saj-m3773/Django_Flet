from rest_framework import serializers
from .models import Product, Specification, Category, Festival, Review
from utils.pricing import calculate_discounted_price
from django.utils import timezone
from datetime import timedelta

# -----------------------------
# Specification
# -----------------------------
class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['title', 'value']

# -----------------------------
# Category
# -----------------------------
class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "icon", "children"]

    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data


class ReviewSerializer(serializers.ModelSerializer):
    # اینجا user فقط نمایش داده میشه، ولی قابل تغییر توسط کاربر نیست
    user = serializers.StringRelatedField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "product", "rating", "text", "created_at",'is_approved']
        read_only_fields = ["id", "user", "product", "created_at",'is_approved']

#send Review
class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["text", "rating"]

    def create(self, validated_data):
        request = self.context.get("request")
        product = self.context.get("product")
        return Review.objects.create(
            user=request.user,
            product=product,
            **validated_data
        )




# -----------------------------
# Product Detail
# -----------------------------
class ProductDetailSerializer(serializers.ModelSerializer):
    specifications = SpecificationSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    discounted_price = serializers.SerializerMethodField()
    festival_discount = serializers.SerializerMethodField()
    discount_duration = serializers.SerializerMethodField()
    time_left = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "price", "discount", "discount_start",
            "discount_duration", "discounted_price", "festival_discount",
            "time_left", "description", "image", "specifications", "categories",'image','reviews'
        ]

    # قیمت نهایی با تخفیف
    def get_discounted_price(self, obj):
        return float(calculate_discounted_price(obj))

    # درصد تخفیف جشنواره فعال
    def get_festival_discount(self, obj):
        now = timezone.now()
        from .models import Festival
        active_festivals = Festival.objects.filter(
            active=True,
            start_date__lte=now,
            end_date__gte=now
        )
        if active_festivals.exists():
            festival = active_festivals.latest("start_date")
            return festival.discount_percentage
        return 0

    # مدت زمان تخفیف محصول
    def get_discount_duration(self, obj):
        return obj.discount_duration or 0

    # زمان باقی‌مانده تخفیف محصول به ثانیه
    def get_time_left(self, obj):
        if obj.discount and obj.discount_start and obj.discount_duration:
            end_time = obj.discount_start + timedelta(hours=obj.discount_duration)
            remaining = end_time - timezone.now()
            return max(int(remaining.total_seconds()), 0)
        return 0

# -----------------------------
# Product برای لیست
# -----------------------------
class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(read_only=True, many=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        source="categories",
        write_only=True
    )
    discounted_price = serializers.SerializerMethodField()
    festival_discount = serializers.SerializerMethodField()
    time_left = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "price",'image', "discount", "discount_start",
            "discount_duration", "discounted_price", "festival_discount",
            "time_left", "categories", "category_ids"
        ]

    def get_discounted_price(self, obj):
        return float(calculate_discounted_price(obj))

    def get_festival_discount(self, obj):
        now = timezone.now()
        from .models import Festival
        active_festivals = Festival.objects.filter(
            active=True,
            start_date__lte=now,
            end_date__gte=now
        )
        if active_festivals.exists():
            festival = active_festivals.latest("start_date")
            return festival.discount_percentage
        return 0

    def get_time_left(self, obj):
        if obj.discount and obj.discount_start and obj.discount_duration:
            end_time = obj.discount_start + timedelta(hours=obj.discount_duration)
            remaining = end_time - timezone.now()
            return max(int(remaining.total_seconds()), 0)
        return 0


