import flet as ft
import requests

from shared.appbar import shared_appbar


def get_register_view(page: ft.Page):
    username = ft.TextField(
        label="نام کاربری",
        prefix_icon=ft.Icons.PERSON,
        text_align=ft.TextAlign.RIGHT,
        filled=True,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=10
    )
    email = ft.TextField(
        label="ایمیل (اختیاری)",
        prefix_icon=ft.Icons.EMAIL,
        text_align=ft.TextAlign.RIGHT,
        filled=True,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=10
    )
    password = ft.TextField(
        label="رمز عبور",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        text_align=ft.TextAlign.RIGHT,
        filled=True,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=10
    )

    message = ft.Text("", color=ft.Colors.RED_600, text_align=ft.TextAlign.RIGHT)

    def handle_register(e):
        data = {
            "username": username.value,
            "email": email.value,
            "password": password.value,
        }
        try:
            response = requests.post("http://127.0.0.1:8000/api/accounts/register/", json=data)
            if response.status_code == 201:
                message.value = "✅ ثبت‌نام با موفقیت انجام شد!"
                message.color = ft.Colors.GREEN
            else:
                errors = response.json()
                message.value = "خطا: " + "; ".join([f"{k}: {v[0]}" for k, v in errors.items()])
                message.color = ft.Colors.RED
        except Exception as err:
            message.value = f"⛔ خطا در ارتباط با سرور: {err}"
            message.color = ft.Colors.RED
        page.update()
        page.go("/login")  # هدایت به صفحه ورود

    form = ft.Column(
        [
            ft.Text("فرم ثبت‌نام", size=26,  weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            username,
            email,
            password,
            ft.FilledButton(
                text="ثبت‌نام",
                icon=ft.Icons.CHECK_CIRCLE,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.BLUE_600,
                    color=ft.Colors.WHITE,
                    padding=10,
                    shape=ft.RoundedRectangleBorder(radius=10)
                ),
                on_click=handle_register
            ),
            message,
            ft.TextButton(
                "⬅ بازگشت به صفحه اصلی",
                icon=ft.Icons.HOME,
                on_click=lambda e: page.go("/"),
            ),
        ],
        width=400,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=15
    )

    return ft.View(
        route="/register",
        appbar=ft.AppBar(
            title=ft.Text("ثبت‌نام کاربر", color=ft.Colors.WHITE),
            leading=ft.Icon(name=ft.Icons.PERSON_ADD, color=ft.Colors.WHITE),
            center_title=True,
            bgcolor=ft.Colors.BLUE_600,
            elevation=4
        ),
        controls=[
            shared_appbar(page),
            ft.Container(content=form, alignment=ft.alignment.center, expand=True)
        ],
        padding=30,
        bgcolor=ft.Colors.WHITE
    )
