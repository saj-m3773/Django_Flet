import flet as ft
import requests
from shared.appbar import shared_appbar  # استفاده از AppBar داینامیک

API_BASE = "http://127.0.0.1:8000/api/accounts/profile/"

def get_profile_view(page: ft.Page, nav):
    profile_data = {}
    token = page.session.get("access")  # گرفتن توکن از session

    if not token:
        # اگر توکن نبود، کاربر هدایت شود به صفحه لاگین
        page.go("/login")
        page.update()
        return

    try:
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(API_BASE, headers=headers)
        if res.status_code == 200:
            profile_data = res.json()
            print("✅ پاسخ سرور:", profile_data)
        else:
            profile_data = {"error": f"خطا در دریافت پروفایل: {res.status_code}"}
            print(profile_data)
    except Exception as e:
        profile_data = {"error": str(e)}
        print("⛔ خطا در ارتباط با سرور:", e)

    # --- دکمه‌ها ---
    btn_home = ft.ElevatedButton(
        "🏠 صفحه اصلی",
        on_click=lambda e: page.go("/"),
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            padding=ft.Padding(20, 10, 20, 10),
        ),
    )

    btn_edit = ft.ElevatedButton(
        "✏️ ویرایش پروفایل",
        on_click=lambda e: page.go("/dashboard/edit-profile"),
        bgcolor=ft.Colors.GREEN_600,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            padding=ft.Padding(20, 10, 20, 10),
        ),
    )

    btn_back = ft.ElevatedButton("⬅️ عقب", on_click=lambda e: nav.go_back())
    btn_forward = ft.ElevatedButton("➡️ جلو", on_click=lambda e: nav.go_forward())

    # --- کارت نمایش اطلاعات ---
    card_content = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON, color="blue"),
                        ft.Text(f"نام کاربری: {profile_data.get('username', '')}")
                    ]),
                    ft.Row([
                        ft.Icon(ft.Icons.EMAIL, color="green"),
                        ft.Text(f"ایمیل: {profile_data.get('email', '')}")
                    ]),
                    ft.Row([
                        ft.Icon(ft.Icons.BADGE, color="purple"),
                        ft.Text(f"نام: {profile_data.get('first_name', '')} {profile_data.get('last_name', '')}")
                    ]),
                    ft.Text(
                        profile_data.get("error", ""),
                        color=ft.Colors.RED_400
                    ),
                    # دکمه‌ها وسط صفحه
                    ft.Row([btn_home, btn_edit], alignment=ft.MainAxisAlignment.CENTER, spacing=30),
                    ft.Row([btn_back, btn_forward], alignment=ft.MainAxisAlignment.CENTER, spacing=30)
                ]
            )
        )
    )

    # --- View کامل ---
    return ft.View(
        "/dashboard/profile",
        controls=[
            shared_appbar(page),  # استفاده از AppBar داینامیک
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    spacing=30,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("اطلاعات کاربر", size=24, weight=ft.FontWeight.BOLD),
                        card_content,
                    ]
                )
            ),
        ]
    )
