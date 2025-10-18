import flet as ft
import requests
from shared.appbar import shared_appbar

API_BASE = "http://127.0.0.1:8000/accounts/api"

def reset_password_view(page: ft.Page, token: str):
    pass_field = ft.TextField(label="رمز عبور جدید", password=True, can_reveal_password=True)
    result_text = ft.Text("", color=ft.Colors.GREEN)

    def send_request(e):
        try:
            r = requests.post(f"{API_BASE}/forgot-password/{token}/", json={"password": pass_field.value})
            if r.status_code == 200:
                result_text.value = "رمز عبور با موفقیت تغییر یافت"
                result_text.color = ft.Colors.GREEN
            else:
                result_text.value = r.json().get("error", "خطا در تغییر رمز")
                result_text.color = ft.Colors.RED
            page.update()
        except:
            result_text.value = "خطا در اتصال به سرور"
            result_text.color = ft.Colors.RED
            page.update()

    return ft.View(
        route=f"/forgot-password/{token}",
        controls=[
            shared_appbar(page),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("تغییر رمز عبور", size=24, weight=ft.FontWeight.BOLD),
                        pass_field,
                        ft.ElevatedButton("ذخیره رمز جدید", icon=ft.Icons.LOCK, on_click=send_request),
                        result_text
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                padding=20
            )
        ]
    )
