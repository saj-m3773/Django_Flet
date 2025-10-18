import flet as ft
import requests
from shared.appbar import shared_appbar


def get_login_view(page: ft.Page):
    username = ft.TextField(
        label="نام کاربری",
        hint_text="نام کاربری خود را وارد کنید",
        prefix_icon=ft.Icons.PERSON,
        text_align=ft.TextAlign.RIGHT,
        border_radius=12,
        bgcolor=ft.Colors.GREY_900,
        color=ft.Colors.WHITE,
    )
    password = ft.TextField(
        label="رمز عبور",
        hint_text="رمز عبور خود را وارد کنید",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        text_align=ft.TextAlign.RIGHT,
        border_radius=12,
        bgcolor=ft.Colors.GREY_900,
        color=ft.Colors.WHITE,
    )

    message = ft.Text("", color=ft.Colors.RED_400)

    def handle_login(e):
        if not username.value or not password.value:
            message.value = "❌ لطفاً نام کاربری و رمز عبور را وارد کنید"
            message.color = ft.Colors.RED_400
            page.update()
            return

        data = {"username": username.value, "password": password.value}
        try:
            response = requests.post("http://127.0.0.1:8000/api/accounts/token/", json=data)
            if response.status_code == 200:
                tokens = response.json()
                # ✅ ذخیره توکن‌ها در session برای هماهنگی با AppBar
                page.session.set("access", tokens["access"])
                page.session.set("refresh", tokens["refresh"])

                message.value = "✅ ورود موفق!"
                message.color = ft.Colors.GREEN_400
                page.update()

                # هدایت به داشبورد
                page.go("/dashboard")
            else:
                message.value = "❌ نام کاربری یا رمز عبور اشتباه است"
                message.color = ft.Colors.RED_400
                page.update()
        except Exception as err:
            message.value = f"⛔ خطا در ارتباط با سرور: {err}"
            message.color = ft.Colors.RED_400
            page.update()

    form = ft.Column(
        [
            ft.Icon(ft.Icons.LOGIN, size=80, color=ft.Colors.BLUE_400),
            ft.Text(
                "ورود به حساب کاربری",
                size=26,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
                color=ft.Colors.WHITE,
            ),
            username,
            password,
            ft.ElevatedButton(
                "ورود",
                icon=ft.Icons.LOGIN,
                icon_color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_500,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                on_click=handle_login,
            ),
            message,
            ft.Row(
                [
                    ft.TextButton("ثبت‌نام", on_click=lambda e: page.go("/register")),
                    ft.TextButton("فراموشی رمز عبور", on_click=lambda e: page.go("/forgot-password")),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ],
        width=400,
        spacing=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    return ft.View(
        route="/login",
        controls=[
            shared_appbar(page),
            ft.Container(
                content=form,
                alignment=ft.alignment.center,
                expand=True,
                bgcolor=ft.Colors.BLACK,
                padding=30,
            ),
        ],
    )
