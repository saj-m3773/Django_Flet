import flet as ft
import requests
from shared.appbar import shared_appbar

API_BASE = "http://127.0.0.1:8000/api"


def get_orders_view(page: ft.Page):
    orders_column = ft.Column(spacing=15)

    def load_orders():
        orders_column.controls.clear()
        token = page.session.get("access")
        if not token:
            page.snack_bar = ft.SnackBar(ft.Text("🔒 ابتدا وارد شوید"))
            page.snack_bar.open = True
            page.update()
            page.go("/login")
            return

        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(f"{API_BASE}/orders/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if not data:
                    orders_column.controls.append(ft.Text("📭 هیچ سفارشی ثبت نشده"))
                else:
                    for order in data:
                        order_box = ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(f"🆔 سفارش: {order['id']}", weight=ft.FontWeight.BOLD),
                                    ft.Text(f"📅 تاریخ: {order['created_at']}"),
                                    ft.Text(f"💰 مبلغ: {order['total_price']:,.0f} تومان"),
                                    ft.Text(f"📦 وضعیت: {order['status']}"),
                                ],
                                spacing=5,
                            ),
                            padding=10,
                            border=ft.border.all(1, ft.Colors.GREY),
                            border_radius=10,
                        )
                        orders_column.controls.append(order_box)
            else:
                orders_column.controls.append(ft.Text("❌ خطا در دریافت سفارش‌ها"))
        except Exception as ex:
            orders_column.controls.append(ft.Text(f"❌ خطا: {ex}"))
        page.update()

    load_orders()

    return ft.View(
        route="/orders",
        appbar=shared_appbar(page),
        padding=20,
        scroll=ft.ScrollMode.AUTO,
        controls=[orders_column],
    )
