import flet as ft
import requests
from get_base64_image import get_base64_image
from decimal import Decimal
from shared.price_label import price_label
API_PRODUCTS = "http://127.0.0.1:8000/api/products/"

def product_card(product, page: ft.Page):
    image_url = product.get("image")
    image_data = get_base64_image(image_url) if image_url else None

    image_control = (
        ft.Image(
            src_base64=image_data,
            width=160,
            height=160,
            fit=ft.ImageFit.CONTAIN,
            border_radius=ft.border_radius.all(12),
        )
        if image_data
        else ft.Container(
            content=ft.Text("❌ تصویر موجود نیست", color=ft.Colors.RED),
            alignment=ft.alignment.center,
            width=160,
            height=160,
        )
    )

    # قیمت‌ها
    original_price = Decimal(product["price"])
    discounted_price = Decimal(product.get("discounted_price", product["price"]))

    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    image_control,
                    ft.Text(
                        product["name"],
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        max_lines=2,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(
                        content=price_label(float(original_price), float(discounted_price)),
                        padding=ft.padding.symmetric(vertical=4),
                        alignment=ft.alignment.center,
                    ),
                    ft.ElevatedButton(
                        text="مشاهده جزئیات",
                        icon=ft.Icons.PAGEVIEW_OUTLINED,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=6),
                        ),
                        on_click=lambda e, pid=product["id"]: page.go(f"/product/{pid}"),
                    ),
                ],
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=12,
            width=220,
            border_radius=ft.border_radius.all(12),  # ✅ اینجا
        ),
        elevation=4,
        margin=ft.margin.all(6),
    )


def set_products(page: ft.Page, products_container: ft.Container, back_button_container: ft.Container, category_slug=None):
    try:
        url = f"http://127.0.0.1:8000/api/categories/{category_slug}/products/" if category_slug else API_PRODUCTS
        res = requests.get(url)
        res.raise_for_status()
        products = res.json()

        product_cards = [product_card(p, page) for p in products]

        # دکمه همه محصولات
        if category_slug:
            back_button_container.content = ft.ElevatedButton(
                text="🛒 همه محصولات",
                icon=ft.Icons.HOME,
                on_click=lambda e: set_products(page, products_container, back_button_container),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=6),
                    bgcolor=ft.Colors.BLUE_500,
                    color=ft.Colors.WHITE,
                ),
            )
        else:
            back_button_container.content = None

        products_container.content = ft.Column(
            [
                back_button_container,
                ft.Text("🛍 محصولات", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            content=card,
                            col={"xs": 12, "sm": 6, "md": 4, "lg": 3, "xl": 2},
                            alignment=ft.alignment.center,
                        )
                        for card in product_cards
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    run_spacing=10,
                ),
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        page.update()
    except Exception as e:
        products_container.content = ft.Text(f"❌ خطا در دریافت محصولات: {e}", color=ft.Colors.RED_700)
        page.update()
