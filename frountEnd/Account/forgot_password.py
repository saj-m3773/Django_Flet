import flet as ft
import requests
from shared.appbar import shared_appbar

API_BASE = "http://127.0.0.1:8000/api/accounts"

def forgot_password_view(page: ft.Page):
    email_field = ft.TextField(label="ایمیل", icon=ft.Icons.EMAIL)
    result_text = ft.Text("", color=ft.Colors.GREEN)

    def send_request(e):
        try:
            r = requests.post(f"{API_BASE}/forgot-password/", json={"email": email_field.value})
            if r.status_code == 200:
                result_text.value = "ایمیل بازیابی ارسال شد."
                result_text.color = ft.Colors.GREEN
            else:
                result_text.value = r.json().get("error", "خطا در ارسال درخواست")
                result_text.color = ft.Colors.RED
            page.update()
        except:
            result_text.value = "خطا در اتصال به سرور"
            result_text.color = ft.Colors.RED
            page.update()

    return ft.View(
        route="/forgot-password",
        controls=[
            shared_appbar(page),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("بازیابی رمز عبور", size=24, weight=ft.FontWeight.BOLD),
                        email_field,
                        ft.ElevatedButton("ارسال ایمیل بازیابی", icon=ft.Icons.SEND, on_click=send_request),
                        result_text
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                padding=20
            )
        ]
    )
