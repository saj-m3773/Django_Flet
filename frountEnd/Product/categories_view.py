import flet as ft
import requests

from get_base64_image import get_base64_image
from shared.appbar import shared_appbar
from shared.price_label import price_label

API_CATEGORIES = "http://127.0.0.1:8000/api/categories/"
API_PRODUCTS = "http://127.0.0.1:8000/api/products/"


def category_card(cat, page, on_click=None):
    """
    کارت دسته‌بندی، با قابلیت callback برای نمایش محصولات دسته انتخاب شده
    """
    image_url = cat.get("icon")
    image_data = get_base64_image(image_url) if image_url else None

    image_control = (
        ft.Image(
            src_base64=image_data,
            width=60,
            height=60,
            fit=ft.ImageFit.CONTAIN,
        )
        if image_data
        else ft.Icon(ft.Icons.CATEGORY, size=40, color=ft.Colors.GREY_600)
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                image_control,
                ft.Text(
                    cat["name"],
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=8,
        on_click=on_click,
    )


def get_parent_categories():
    try:
        res = requests.get(API_CATEGORIES)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("❌ خطا در دریافت دسته‌بندی‌ها:", e)
        return []


def get_category_detail(slug):
    try:
        res = requests.get(f"{API_CATEGORIES}{slug}/")
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print("Error:", e)
    return {}


def get_products(category_slug=None):
    """
    دریافت محصولات دسته اصلی + زیرمجموعه‌ها
    """
    try:
        if category_slug:
            url = f"http://127.0.0.1:8000/api/categories/{category_slug}/products/"
        else:
            url = API_PRODUCTS  # همه محصولات

        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("Error fetching products:", e)
        return []



def get_product_card(product, page):
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

    # ------------------ قیمت ------------------
    price_display = price_label(
        original_price=float(product["price"]),
        discounted_price=float(product.get("discounted_price", product["price"]))
    ).get_control()

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
                    price_display,  # ✅ جایگزین شد
                    ft.ElevatedButton(
                        text="مشاهده جزئیات",
                        icon=ft.Icons.PAGEVIEW_OUTLINED,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=6),
                        ),
                        on_click=lambda e, pid=product["id"]: page.go(f"/product/{pid}"),
                    ),
                ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=12,
            width=220,
        ),
        elevation=3,
        margin=ft.margin.all(6),
    )


def get_category_view(page: ft.Page, slug=None):
    """
    صفحه دسته‌بندی واقعی: دسته انتخاب شده + زیرمجموعه + محصولات
    """
    view = ft.View("/", scroll=ft.ScrollMode.AUTO, appbar=shared_appbar(page), controls=[])

    selected_category = {}
    subcategories_container = ft.Container()
    products_container = ft.Container()

    # تابع لود محصولات دسته انتخاب شده
    def load_category(cat_slug):
        nonlocal selected_category
        selected_category = get_category_detail(cat_slug)

        # زیرمجموعه‌ها
        subcats = selected_category.get("children", [])

        if subcats:
            row = ft.Row(
                controls=[
                    category_card(
                        sub,
                        page,
                        on_click=lambda e, s=sub: load_category(s["slug"])
                    )
                    for sub in subcats
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=12,
                alignment=ft.MainAxisAlignment.CENTER,
            )
            subcategories_container.content = ft.Column(
                [
                    ft.Text("زیرمجموعه‌ها", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    row
                ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        else:
            subcategories_container.content = None

        # محصولات دسته اصلی + زیرمجموعه‌ها
        products = get_products(cat_slug)
        product_cards = [get_product_card(p, page) for p in products]

        products_container.content = ft.Column(
            [
                ft.Text(
                    f"🛍 محصولات دسته: {selected_category.get('name','')}",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
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

    # دسته‌های اصلی
    parent_categories = get_parent_categories()
    if parent_categories:
        row = ft.Row(
            controls=[
                category_card(
                    cat,
                    page,
                    on_click=lambda e, slug=cat["slug"]: load_category(slug)
                )
                for cat in parent_categories
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        view.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("📂 دسته‌بندی‌ها", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        row
                    ],
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(10),
                alignment=ft.alignment.center,
            )
        )

    # اضافه کردن کانتینر زیرمجموعه‌ها و محصولات
    view.controls.append(subcategories_container)
    view.controls.append(products_container)

    # بارگذاری پیش‌فرض: همه محصولات
    load_category(slug if slug else parent_categories[0]["slug"])

    return view
