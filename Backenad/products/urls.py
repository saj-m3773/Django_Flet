from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductDetailView, CategoryListView, ProductByCategoryView, ReviewListCreateView

router = DefaultRouter()
router.register(r'products', ProductViewSet)
urlpatterns = [
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path("products/<int:product_id>/reviews/", ReviewListCreateView.as_view(), name="product-reviews"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/<slug:slug>/products/", ProductByCategoryView.as_view(), name="products-by-category"),
]

urlpatterns += router.urls
