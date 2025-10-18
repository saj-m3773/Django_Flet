from decimal import Decimal
from django.utils import timezone

def calculate_discounted_price(product) -> Decimal:

    # ایمپورت درون تابع برای جلوگیری از circular import
    from products.models import Festival

    price: Decimal = product.price
    now = timezone.now()

    # بررسی جشنواره فعال
    active_festivals = Festival.objects.filter(
        active=True,
        start_date__lte=now,
        end_date__gte=now
    )
    if active_festivals.exists():
        festival = active_festivals.latest("start_date")
        discount_factor = Decimal(1 - festival.discount_percentage / 100)
        return price * discount_factor

    # بررسی تخفیف محصول زمان‌دار
    if product.discount and product.discount_start and product.discount_duration:
        discount_end = product.discount_start + timezone.timedelta(hours=product.discount_duration)
        if product.discount_start <= now <= discount_end:
            discount_factor = Decimal(1 - product.discount / 100)
            return price * discount_factor

    return price
