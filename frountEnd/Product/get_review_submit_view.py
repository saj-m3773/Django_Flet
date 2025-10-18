import flet as ft
import requests

API_BASE = "http://127.0.0.1:8000/api"


def get_review_submit_view(page: ft.Page, product_id):
    """
    ویوی مجزا برای ارسال نظر با استفاده از توکن ذخیره شده در session
    """

    # گرفتن access_token از session
    user_token = page.session.get("access")

    if not user_token:
        page.snack_bar = ft.SnackBar(ft.Text("⚠️ برای ارسال نظر باید وارد شوید"))
        page.snack_bar.open = True
        page.update()
        page.go("/login")
        return ft.View(route="/login", controls=[])

    # ------------------ فرم ارسال نظر ------------------
    rating_dropdown = ft.Dropdown(
        label="امتیاز شما",
        options=[
            ft.dropdown.Option("1", "⭐ 1"),
            ft.dropdown.Option("2", "⭐⭐ 2"),
            ft.dropdown.Option("3", "⭐⭐⭐ 3"),
            ft.dropdown.Option("4", "⭐⭐⭐⭐ 4"),
            ft.dropdown.Option("5", "⭐⭐⭐⭐⭐ 5"),
        ],
        width=200
    )

    review_input = ft.TextField(
        label="نظر شما",
        multiline=True,
        min_lines=3,
        max_lines=5,
        width=400
    )

    # ------------------ تابع ارسال نظر ------------------
    def submit_review(e):
        rating = int(rating_dropdown.value or 0)
        text = review_input.value.strip()

        if not rating or not text:
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ لطفا امتیاز و متن نظر را وارد کنید"))
            page.snack_bar.open = True
            page.update()
            return

        try:
            headers = {
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "application/json",
            }
            payload = {"rating": rating, "text": text}

            response = requests.post(
                f"{API_BASE}/products/{product_id}/reviews/",
                json=payload,
                headers=headers
            )

            if response.status_code == 201:
                # نمایش SnackBar
                page.snack_bar = ft.SnackBar(
                    ft.Text("✅ نظر شما با موفقیت ثبت شد و بعد از تایید نمایش داده می‌شود."),
                    duration=3000  # میلی‌ثانیه، 3 ثانیه نمایش
                )
                page.snack_bar.open = True
                page.update()

                # هدایت بعد از 3 ثانیه
                def go_back(_):
                    page.go(f"/product/{product_id}")

                page.snack_bar.on_dismiss = go_back

            elif response.status_code == 401:
                page.snack_bar = ft.SnackBar(ft.Text("❌ احراز هویت ناموفق! لطفا دوباره وارد شوید"))
                page.snack_bar.open = True
                page.update()
                page.go("/login")
            else:
                error = response.json().get("error", "❌ خطا در ارسال نظر")
                page.snack_bar = ft.SnackBar(ft.Text(error))
                page.snack_bar.open = True
                page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ خطا: {ex}"))
            page.snack_bar.open = True
            page.update()

    # ------------------ دکمه‌ها ------------------
    submit_button = ft.ElevatedButton(
        "ثبت نظر",
        icon=ft.Icons.SEND,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
        on_click=submit_review
    )

    back_button = ft.ElevatedButton(
        "بازگشت به محصول",
        icon=ft.Icons.ARROW_BACK,
        on_click=lambda e: page.go(f"/product/{product_id}")
    )

    # ------------------ ویو ------------------
    return ft.View(
        route=f"/product/{product_id}/review",
        controls=[
            ft.Text("✍️ ثبت نظر جدید", size=20, weight=ft.FontWeight.BOLD),
            rating_dropdown,
            review_input,
            ft.Row(controls=[submit_button, back_button], alignment=ft.MainAxisAlignment.END)
        ],
        padding=20,
        scroll=ft.ScrollMode.AUTO
    )
