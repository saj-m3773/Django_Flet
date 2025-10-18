import flet as ft
import requests
from decimal import Decimal
from shared.appbar import shared_appbar
from shared.price_label import price_label

API_BASE = "http://127.0.0.1:8000/api"


def get_cart_view(page: ft.Page):
    cart_column = ft.Column(spacing=15)

    def load_cart():
        cart_column.controls.clear()
        token = page.session.get("access")

        if not token:
            page.snack_bar = ft.SnackBar(ft.Text("🔒 لطفا ابتدا وارد حساب شوید"))
            page.snack_bar.open = True
            page.update()
            page.go("/login")
            return

        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.get(f"{API_BASE}/cart/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                total_price = Decimal("0")

                if not items:
                    cart_column.controls.append(ft.Text("🛒 سبد خرید شما خالی است", size=18))
                else:
                    for item in items:
                        product = item["product"]
                        quantity = int(item["quantity"])
                        original_price = Decimal(product["price"])
                        discounted_price = Decimal(product.get("discounted_price", product["price"]))
                        final_price = discounted_price * quantity
                        total_price += final_price

                        # هندلرهای داینامیک
                        def make_remove_handler(item_id):
                            return lambda e: remove_item(item_id)

                        def make_increase_handler(item_id, q):
                            return lambda e: update_quantity(item_id, q + 1)

                        def make_decrease_handler(item_id, q):
                            return lambda e: update_quantity(item_id, q - 1)

                        # ردیف آیتم
                        item_row = ft.Row(
                            controls=[
                                ft.Text(product["name"], weight=ft.FontWeight.BOLD, width=200),
                                price_label(float(original_price), float(discounted_price)),
                                ft.Row(
                                    controls=[
                                        ft.TextButton("➖", on_click=make_decrease_handler(item["id"], quantity)),
                                        ft.Text(str(quantity), width=30, text_align=ft.TextAlign.CENTER),
                                        ft.TextButton("➕", on_click=make_increase_handler(item["id"], quantity)),
                                    ]
                                ),
                                ft.ElevatedButton(
                                    "❌ حذف",
                                    bgcolor=ft.Colors.RED,
                                    color=ft.Colors.WHITE,
                                    on_click=make_remove_handler(item["id"]),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            spacing=10,
                        )
                        cart_column.controls.append(item_row)

                    # جمع کل + دکمه پرداخت
                    cart_column.controls.append(
                        ft.Row(
                            controls=[
                                ft.Text(f"💰 جمع کل: {total_price:,.0f} تومان", size=18, weight=ft.FontWeight.BOLD),
                                ft.ElevatedButton(
                                    "💳 پرداخت",
                                    bgcolor=ft.Colors.GREEN,
                                    color=ft.Colors.WHITE,
                                    on_click=start_checkout,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        )
                    )
            elif response.status_code == 401:
                page.snack_bar = ft.SnackBar(ft.Text("❌ توکن نامعتبر یا منقضی شده"))
                page.snack_bar.open = True
                page.update()
                page.go("/login")
            else:
                cart_column.controls.append(ft.Text("❌ خطا در دریافت سبد خرید"))
            page.update()
        except Exception as ex:
            cart_column.controls.append(ft.Text(f"❌ خطا: {ex}"))
            page.update()

    def remove_item(cart_item_id):
        token = page.session.get("access")
        if not token:
            page.snack_bar = ft.SnackBar(ft.Text("🔒 لطفا ابتدا وارد حساب شوید"))
            page.snack_bar.open = True
            page.update()
            page.go("/login")
            return

        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.delete(f"{API_BASE}/cart/item/{cart_item_id}/delete/", headers=headers)
            if response.status_code == 204:
                page.snack_bar = ft.SnackBar(ft.Text("✅ آیتم حذف شد"))
                page.snack_bar.open = True
                load_cart()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("❌ خطا در حذف آیتم"))
                page.snack_bar.open = True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ خطا: {ex}"))
            page.snack_bar.open = True
            page.update()

    def update_quantity(cart_item_id, new_quantity):
        token = page.session.get("access")
        if not token:
            page.snack_bar = ft.SnackBar(ft.Text("🔒 لطفا ابتدا وارد حساب شوید"))
            page.snack_bar.open = True
            page.update()
            page.go("/login")
            return

        headers = {"Authorization": f"Bearer {token}"}
        if new_quantity < 1:
            remove_item(cart_item_id)
            return

        try:
            response = requests.patch(f"{API_BASE}/cart/item/{cart_item_id}/update/", headers=headers, json={"quantity": new_quantity})
            if response.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("✅ تعداد بروزرسانی شد"))
                page.snack_bar.open = True
                load_cart()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("❌ خطا در بروزرسانی تعداد"))
                page.snack_bar.open = True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ خطا: {ex}"))
            page.snack_bar.open = True
            page.update()

    def start_checkout(e):
        """هدایت به ویو checkout برای پرداخت"""
        page.go("/checkout")

    # بارگذاری اولیه
    load_cart()

    return ft.View(
        route="/cart",
        appbar=shared_appbar(page),
        scroll=ft.ScrollMode.AUTO,
        padding=20,
        controls=[ft.Column(controls=[cart_column], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.END)],
    )
