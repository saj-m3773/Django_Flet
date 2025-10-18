import flet as ft
from shared.appbar import shared_appbar
from Product.categories_view import get_parent_categories, category_card
from Product.products_view import set_products

def get_product_list_view(page: ft.Page):
    view = ft.View("/", scroll=ft.ScrollMode.AUTO, appbar=shared_appbar(page), controls=[])

    # کانتینر محصولات و دکمه برگشت
    products_container = ft.Container()
    back_button_container = ft.Container()

    # دسته‌بندی‌ها
    parent_categories = get_parent_categories()
    if parent_categories:
        def on_category_click(cat_slug):
            set_products(page, products_container, back_button_container, cat_slug)

        cat_row = ft.Row(
            controls=[ft.Container(content=category_card(cat, page), on_click=lambda e, slug=cat["slug"]: on_category_click(slug)) for cat in parent_categories],
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        view.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("📂 دسته‌بندی‌ها", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        cat_row,
                    ],
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(10),
                alignment=ft.alignment.center,
            )
        )

    # اضافه کردن کانتینر محصولات
    view.controls.append(products_container)

    # بارگذاری محصولات همه دسته‌ها به صورت پیش‌فرض
    set_products(page, products_container, back_button_container)

    return view
