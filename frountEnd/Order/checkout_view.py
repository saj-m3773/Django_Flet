import flet as ft
import requests
from shared.appbar import shared_appbar

API_BASE = "http://127.0.0.1:8000/api"


def get_checkout_view(page: ft.Page):
    # ✅ خواندن داده‌ها از session به‌صورت ایمن
    total_price = page.session.get("total_price") or 0
    order_id = page.session.get("order_id")

    column = ft.Column(spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # 🧾 اگر اطلاعات ناقص بود
    if not order_id or total_price == 0:
        column.controls.append(
            ft.Text("❌ اطلاعات پرداخت یافت نشد!", size=18, color=ft.Colors.RED)
        )
        column.controls.append(
            ft.ElevatedButton("بازگشت به سبد خرید", on_click=lambda e: page.go("/cart"))
        )
        return ft.View(
            route="/checkout",
            appbar=shared_appbar(page),
            controls=[column],
            padding=20,
        )

    # 💳 تابع شروع پرداخت
    def start_payment(e):
        token = page.session.get("access")
        if not token:
            page.snack_bar = ft.SnackBar(ft.Text("🔒 لطفاً ابتدا وارد حساب شوید"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            page.go("/login")
            return

        headers = {"Authorization": f"Bearer {token}"}

        try:
            # ارسال درخواست ایجاد پرداخت به بک‌اند
            response = requests.post(f"{API_BASE}/orders/{order_id}/payment/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                authority = data.get("authority")

                if authority:
                    # لینک درگاه پرداخت (زیر نمونه زرین‌پال / شاپرک)
                    payment_url = f"https://sandbox.zarinpal.com/pg/StartPay/{authority}"
                    page.launch_url(payment_url)
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("❌ لینک پرداخت معتبر نیست"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("❌ خطا در شروع پرداخت"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ خطای شبکه: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    # 🧩 نمایش جزئیات پرداخت
    column.controls.append(
        ft.Text("💳 مرحله پرداخت", size=22, weight=ft.FontWeight.BOLD)
    )
    column.controls.append(
        ft.Text(f"مبلغ قابل پرداخت: {total_price:,.0f} تومان", size=18)
    )
    column.controls.append(
        ft.Row(
            controls=[
                ft.ElevatedButton(
                    "✅ تایید و پرداخت",
                    bgcolor=ft.colors.GREEN,
                    color=ft.colors.WHITE,
                    on_click=start_payment,
                    width=200,
                ),
                ft.OutlinedButton(
                    "بازگشت به سبد خرید",
                    on_click=lambda e: page.go("/cart"),
                    width=200,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )
    )

    return ft.View(
        route="/checkout",
        appbar=shared_appbar(page),
        scroll=ft.ScrollMode.AUTO,
        padding=30,
        controls=[column],
    )
