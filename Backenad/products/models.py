from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from utils.pricing import calculate_discounted_price


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )
    icon = models.ImageField(upload_to="category_icons/", null=True, blank=True)  # آیکون دسته‌بندی

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["parent__id", "name"]

    def __str__(self):
        return self.name


class Festival(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام جشنواره")
    discount_percentage = models.PositiveIntegerField(verbose_name="درصد تخفیف")
    start_date = models.DateTimeField(verbose_name="تاریخ شروع")
    end_date = models.DateTimeField(verbose_name="تاریخ پایان")
    active = models.BooleanField(default=True, verbose_name="فعال")

    def __str__(self):
        return self.name

    def is_active(self):
        now = timezone.now()
        return self.active and self.start_date <= now <= self.end_date



from django.db import models
from django.utils import timezone

class Product(models.Model):
    DISCOUNT_CHOICES = [
        (0, "بدون تخفیف"),
        (10, "۱۰٪"),
        (20, "۲۰٪"),
        (30, "۳۰٪"),
        (50, "تخفیف ویژه ۵۰٪"),
        (60, "تخفیف ویژه ۶۰٪"),
        (80, "تخفیف ویژه ۸۰٪"),
    ]

    DURATION_CHOICES = [
        (2, "۲ ساعت"),
        (24, "۲۴ ساعت"),
        (48, "۴۸ ساعت"),
    ]

    name = models.CharField(max_length=100, verbose_name='نام')
    slug = models.CharField(max_length=100, verbose_name='slug')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قیمت')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    image = models.ImageField(upload_to='images/products', null=True, blank=True, verbose_name='تصویر محصول')
    categories = models.ManyToManyField("Category", related_name="products", verbose_name='دسته بندی')
    discount = models.IntegerField(choices=DISCOUNT_CHOICES, default=0, verbose_name='تخفیف')
    discount_start = models.DateTimeField(null=True, blank=True, verbose_name="شروع تخفیف")
    discount_duration = models.IntegerField(choices=DURATION_CHOICES, null=True, blank=True, verbose_name="مدت زمان تخفیف (ساعت)")

    def __str__(self):
        return self.name


class Specification(models.Model):
    product = models.ForeignKey(Product, related_name='specifications', on_delete=models.CASCADE,verbose_name='محصول')
    title = models.CharField(max_length=100,verbose_name='عنوان')
    value = models.CharField(max_length=255,verbose_name='مقدار')

    def __str__(self):
        return f"{self.title}: {self.value}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"