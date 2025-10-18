import flet as ft
import requests
from shared.appbar import shared_appbar

API_BASE = "http://127.0.0.1:8000/api"


def get_payment_result_view(page: ft.Page, authority=None, status=None):
    """
    نمایش نتیجه پرداخت (موفق / ناموفق)
    authority → از درگاه ارسال می‌شود
    status → وضعیت پرداخت (OK یا NOK)
    """

    column = ft.Column(spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # اگر لینک ناقص باشد
    if not authority or not status:
        column.controls.append(
            ft.Text("❌ اطلاعات پرداخت ناقص است!", size=18, color=ft.colors.RED)
        )
        column.controls.append(
            ft.ElevatedButton("بازگشت به سبد خرید", on_click=lambda e: page.go("/cart"))
        )
        return ft.View(route="/payment-result", controls=[column], padding=20)

    # پیام اولیه
    column.controls.append(ft.Text("در حال بررسی وضعیت پرداخت...", size=18))
    loading = ft.ProgressRing(width=50, height=50)
    column.controls.append(loading)
    page.update()

    def verify_payment():
        """بررسی وضعیت پرداخت از بک‌اند"""
        token = page.session.get("access")
        if not token:
            page.go("/login")
            return

        order_id = page.session.get("order_id")
        if not order_id:
            column.controls.clear()
            column.controls.append(
                ft.Text("❌ سفارش یافت نشد!", size=18, color=ft.colors.RED)
            )
            page.update()
            return

        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.post(
                f"{API_BASE}/payments/verify/",
                json={"authority": authority, "status": status, "order_id": order_id},
                headers=headers,
            )
            data = response.json()

            column.controls.clear()

            if response.status_code == 200 and data.get("status") == "success":
                # موفقیت در پرداخت
                column.controls.append(
                    ft.Icon(name=ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN, size=80)
                )
                column.controls.append(
                    ft.Text("✅ پرداخت با موفقیت انجام شد!", size=20, weight=ft.FontWeight.BOLD)
                )
                column.controls.append(
                    ft.Text(f"کد رهگیری: {data.get('ref_id', '---')}", size=16)
                )
                column.controls.append(
                    ft.ElevatedButton("مشاهده سفارش", on_click=lambda e: page.go("/orders"))
                )
            else:
                # شکست در پرداخت
                column.controls.append(
                    ft.Icon(name=ft.icons.ERROR, color=ft.colors.RED, size=80)
                )
                column.controls.append(
                    ft.Text("❌ پرداخت ناموفق بود یا لغو شد!", size=20, weight=ft.FontWeight.BOLD)
                )
                column.controls.append(
                    ft.ElevatedButton("بازگشت به سبد خرید", on_click=lambda e: page.go("/cart"))
                )

            page.update()

        except Exception as ex:
            column.controls.clear()
            column.controls.append(
                ft.Text(f"❌ خطای ارتباط با سرور: {ex}", color=ft.colors.RED)
            )
            column.controls.append(
                ft.ElevatedButton("بازگشت به سبد خرید", on_click=lambda e: page.go("/cart"))
            )
            page.update()

    # اجرای بررسی در Thread جدا
    page.run_thread(verify_payment)

    return ft.View(
        route="/payment-result",
        appbar=shared_appbar(page),
        scroll=ft.ScrollMode.AUTO,
        padding=30,
        controls=[column],
    )
