import flet as ft

def price_label(original_price: float, discounted_price: float = None) -> ft.Row:
    """
    برگرداندن کنترل Row برای نمایش قیمت محصول.
    اگر discounted_price کمتر از original_price باشد،
    قیمت اصلی خط‌خورده و قیمت تخفیف‌خورده قرمز نمایش داده می‌شود.
    """
    if discounted_price is None:
        discounted_price = original_price

    # تبدیل به عدد صحیح و نمایش با جداکننده هزار
    orig_str = f"{int(original_price):,} تومان"
    disc_str = f"{int(discounted_price):,} تومان"

    if discounted_price < original_price:
        row = ft.Row(
            controls=[
                ft.Icon(name=ft.Icons.ATTACH_MONEY, size=24, color=ft.Colors.GREEN_700),
                ft.Text(
                    orig_str,
                    size=20,
                    color=ft.Colors.GREY_700,
                    style=ft.TextStyle(
                        decoration=ft.TextDecoration.LINE_THROUGH,
                        decoration_thickness=2,
                        decoration_color=ft.Colors.GREY_700
                    )
                ),
                ft.Text(
                    disc_str,
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.RED_700
                ),
            ],
            alignment=ft.MainAxisAlignment.END
        )
    else:
        row = ft.Row(
            controls=[
                ft.Icon(name=ft.Icons.ATTACH_MONEY, size=24, color=ft.Colors.GREEN_700),
                ft.Text(orig_str, size=20, weight=ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.END
        )
    return row
