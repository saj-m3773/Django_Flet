from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, permissions, status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response

from products.models import Product, Category, Review
from products.serializers import ProductSerializer, ProductDetailSerializer, CategorySerializer, ReviewSerializer, \
    ReviewCreateSerializer


# -------------------------------
# Product ViewSet
# -------------------------------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# -------------------------------
# Product Detail
# -------------------------------
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        product = self.get_object()

        # 🔹 بررسی تعداد نظرات کاربر برای این محصول
        existing_reviews = Review.objects.filter(product=product, user=request.user).count()
        if existing_reviews >= 2:
            return Response(
                {"detail": "شما قبلاً ۲ نظر برای این محصول ثبت کرده‌اید."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ReviewCreateSerializer(
            data=request.data,
            context={"request": request, "product": product}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            ReviewSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED
        )

# -------------------------------
# دسته‌بندی‌ها
# -------------------------------
class CategoryListView(ListAPIView):
    queryset = Category.objects.filter(parent=None)  # فقط دسته‌های اصلی
    serializer_class = CategorySerializer

# -------------------------------
# جمع‌آوری id دسته و زیرمجموعه‌ها (بازگشتی)
# -------------------------------
def get_all_category_ids(category):
    ids = [category.id]
    for child in category.children.all():
        ids.extend(get_all_category_ids(child))
    return ids

# -------------------------------
# محصولات بر اساس دسته‌بندی
# -------------------------------
class ProductByCategoryView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        category = get_object_or_404(Category, slug=slug)
        category_ids = get_all_category_ids(category)
        # فیلتر محصولات با دسته‌بندی و حذف تکراری‌ها
        return Product.objects.filter(categories__id__in=category_ids).distinct()

class ReviewListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs["product_id"]
        return Review.objects.filter(product_id=product_id, is_approved=True).order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_serializer(self, *args, **kwargs):
        """
        اضافه کردن request و product به context
        """
        kwargs.setdefault("context", {})
        kwargs["context"].update({
            "request": self.request,
            "product": get_object_or_404(Product, id=self.kwargs["product_id"])
        })
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        """
        ذخیره نظر جدید - user و product داخل Serializer ست میشن
        """
        serializer.save()
