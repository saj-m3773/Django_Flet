import flet as ft
import requests
from shared.appbar import shared_appbar

API_PROFILE = "http://127.0.0.1:8000/api/accounts/profile/"

def get_edit_profile_view(page: ft.Page, nav):
    token = page.session.get("access")  # ✅ گرفتن توکن از session
    if not token:
        page.go("/login")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # --- گرفتن اطلاعات فعلی کاربر ---
    try:
        res = requests.get(API_PROFILE, headers=headers)
        if res.status_code == 200:
            user_data = res.json()
        else:
            user_data = {"error": f"خطا در دریافت اطلاعات: {res.status_code}"}
    except Exception as e:
        user_data = {"error": str(e)}

    btn_profile = ft.ElevatedButton(
        "پروفایل",
        on_click=lambda e: page.go("/dashboard/profile"),
        bgcolor=ft.Colors.GREEN_600,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            padding=ft.Padding(20, 10, 20, 10),
        ),
    )

    # --- فرم ---
    username = ft.TextField(label="نام کاربری", value=user_data.get("username", ""))
    email = ft.TextField(label="ایمیل", value=user_data.get("email", ""))
    first_name = ft.TextField(label="نام", value=user_data.get("first_name", ""))
    last_name = ft.TextField(label="نام خانوادگی", value=user_data.get("last_name", ""))
    message = ft.Text("", color=ft.Colors.RED_400)

    def handle_save(e):
        data = {
            "username": username.value,
            "email": email.value,
            "first_name": first_name.value,
            "last_name": last_name.value
        }
        try:
            res = requests.put(API_PROFILE, headers=headers, json=data)
            if res.status_code in [200, 204]:
                message.value = "✅ اطلاعات با موفقیت بروزرسانی شد"
                message.color = ft.Colors.GREEN_400
            else:
                try:
                    err = res.json().get("detail", "مشکل در بروزرسانی")
                except:
                    err = f"خطا {res.status_code}"
                message.value = f"❌ {err}"
                message.color = ft.Colors.RED_400
        except Exception as e:
            message.value = f"⛔ خطا در ارتباط با سرور: {e}"
            message.color = ft.Colors.RED_400
        page.update()

    form = ft.Column(
        [
            ft.Text("ویرایش پروفایل", size=26, weight=ft.FontWeight.BOLD),
            username,
            email,
            first_name,
            last_name,
            ft.ElevatedButton(
                "ذخیره تغییرات",
                on_click=handle_save,
                bgcolor=ft.Colors.BLUE_500,
                color=ft.Colors.WHITE
            ),
            message,
            ft.Row([btn_profile], alignment=ft.MainAxisAlignment.CENTER, spacing=30),
            ft.Row([
                ft.ElevatedButton("⬅️ عقب", on_click=lambda e: nav.go_back()),
                ft.ElevatedButton("➡️ جلو", on_click=lambda e: nav.go_forward()),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        ],
        spacing=20,
        width=400,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    return ft.View(
        "/dashboard/edit-profile",
        controls=[
            shared_appbar(page),
            ft.Container(
                content=form,
                alignment=ft.alignment.center,
                expand=True,
                padding=20,
                bgcolor=ft.Colors.BLACK
            )
        ]
    )
