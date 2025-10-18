import flet as ft
import requests
from get_base64_image import get_base64_image
from shared.appbar import shared_appbar
from shared.countdown_timer import CountdownTimer
from shared.price_label import price_label

API_BASE = "http://127.0.0.1:8000/api"

def get_product_detail_view(page: ft.Page, product_id):
    countdown_timer = None

    def build_view():
        nonlocal countdown_timer

        view = ft.View(
            route=f"/product/{product_id}",
            appbar=shared_appbar(page),
            controls=[],
            padding=30,
            scroll=ft.ScrollMode.AUTO
        )

        try:
            response = requests.get(f"{API_BASE}/products/{product_id}/")
            response.raise_for_status()
            product = response.json()

            image_url = product.get("image")
            image_data = get_base64_image(image_url) if image_url else None

            # ------------------ عنوان ------------------
            header = ft.Row(
                controls=[
                    ft.Text(product['name'], size=30, weight=ft.FontWeight.BOLD),
                    ft.Icon(name=ft.Icons.SHOPPING_BAG, size=30, color=ft.Colors.PURPLE_700),
                ],
                alignment=ft.MainAxisAlignment.END
            )

            # ------------------ تصویر ------------------
            image_control = ft.Image(
                src_base64=image_data,
                width=300,
                height=300,
                fit=ft.ImageFit.CONTAIN,
                border_radius=10,
            ) if image_data else ft.Text("❌ تصویر موجود نیست", size=16)

            # ------------------ قیمت ------------------
            original_price = float(product['price'])
            discounted_price = float(product.get('discounted_price', original_price))
            discount_seconds_left = product.get('time_left', 0)

            price_row = price_label(original_price, discounted_price)

            # ------------------ تایمر معکوس ------------------
            countdown_timer = CountdownTimer(discount_seconds_left)
            countdown_control = countdown_timer.get_control()
            countdown_timer.start(page)

            # ------------------ توضیحات ------------------
            desc_row = ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(name=ft.Icons.DESCRIPTION, size=24, color=ft.Colors.GREY_700),
                            ft.Text("توضیحات:", size=18, weight=ft.FontWeight.BOLD),
                        ],
                        alignment=ft.MainAxisAlignment.END
                    ),
                    ft.Container(
                        content=ft.Text(
                            product['description'],
                            size=16,
                            text_align=ft.TextAlign.RIGHT,
                            selectable=True
                        ),
                        padding=10,
                        width=500,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=8
                    ),
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.END
            )

            # ------------------ مشخصات فنی ------------------
            specs_controls = [
                ft.Row(
                    controls=[
                        ft.Icon(name=ft.Icons.CHECK_CIRCLE_OUTLINE, size=20, color=ft.Colors.BLUE_600),
                        ft.Text(f"{spec['title']}: {spec['value']}", text_align=ft.TextAlign.RIGHT),
                    ],
                    alignment=ft.MainAxisAlignment.END
                ) for spec in product.get("specifications", [])
            ]

            # ------------------ افزودن به سبد خرید ------------------
            user_token = page.session.get("access")

            def add_to_cart(e):
                token = page.session.get("access")  # مشابه login_view
                if not token:
                    page.snack_bar = ft.SnackBar(ft.Text("🔒 لطفا برای افزودن به سبد خرید وارد شوید"))
                    page.snack_bar.open = True
                    page.update()
                    page.go("/login")
                    return

                try:
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    }
                    payload = {"product_id": product_id, "quantity": 1}
                    response = requests.post(f"{API_BASE}/cart/", json=payload, headers=headers)

                    if response.status_code == 200:
                        page.snack_bar = ft.SnackBar(ft.Text("✅ محصول به سبد خرید اضافه شد"))
                    elif response.status_code == 401:
                        page.snack_bar = ft.SnackBar(ft.Text("❌ لطفا دوباره وارد شوید"))
                        page.snack_bar.open = True
                        page.update()
                        page.go("/login")
                        return
                    else:
                        page.snack_bar = ft.SnackBar(ft.Text("❌ خطا در افزودن به سبد خرید"))

                    page.snack_bar.open = True
                    page.update()

                except Exception as ex:
                    page.snack_bar = ft.SnackBar(ft.Text(f"❌ خطا: {ex}"))
                    page.snack_bar.open = True
                    page.update()

            add_to_cart_button = ft.ElevatedButton(
                "🛒 افزودن به سبد خرید",
                icon=ft.Icons.ADD_SHOPPING_CART,
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                on_click=add_to_cart
            )

            # ------------------ نظرات کاربران ------------------
            reviews = product.get("reviews", [])
            review_controls = []

            review_controls.append(
                ft.Row(
                    controls=[
                        ft.Icon(name=ft.Icons.REVIEWS, size=24, color=ft.Colors.AMBER),
                        ft.Text("نظرات کاربران", size=20, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.END
                )
            )

            if reviews:
                for review in reviews:
                    stars = ft.Row(
                        controls=[
                            ft.Icon(name=ft.Icons.STAR, size=18, color=ft.Colors.AMBER)
                            for _ in range(int(review.get("rating", 0)))
                        ],
                        spacing=2,
                        alignment=ft.MainAxisAlignment.START
                    )
                    review_controls.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text(f"👤 {review['user']}", weight=ft.FontWeight.BOLD, size=14),
                                                ft.Text(f"📅 {review['created_at']}", size=12, color=ft.Colors.GREY_600),
                                            ],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                        ),
                                        stars,
                                        ft.Text(
                                            review["text"],
                                            selectable=True,
                                            size=14,
                                            text_align=ft.TextAlign.RIGHT
                                        ),
                                    ],
                                    spacing=8,
                                    horizontal_alignment=ft.CrossAxisAlignment.END
                                ),
                                padding=15
                            ),
                            elevation=2,
                            margin=ft.margin.all(5),
                            shape=ft.RoundedRectangleBorder(radius=12),
                        )
                    )
            else:
                review_controls.append(
                    ft.Text("❌ هنوز نظری ثبت نشده است.", size=14, italic=True, text_align=ft.TextAlign.RIGHT)
                )

            # ------------------ فرم ثبت نظر ------------------
            user_token = page.session.get("access")
            if user_token:
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
                            # نمایش پیام تایید
                            page.snack_bar = ft.SnackBar(
                                ft.Text("✅ نظر شما با موفقیت ثبت شد و بعد از تایید نمایش داده می‌شود."),
                                duration=3000
                            )
                            page.snack_bar.open = True
                            page.update()
                            # پاک کردن فرم
                            rating_dropdown.value = None
                            review_input.value = ""
                            page.update()
                        elif response.status_code == 401:
                            page.snack_bar = ft.SnackBar(ft.Text("❌ لطفا دوباره وارد شوید"))
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

                submit_button = ft.ElevatedButton(
                    "ثبت نظر",
                    icon=ft.Icons.SEND,
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                    on_click=submit_review
                )

                review_controls.append(
                    ft.Card(
                        content=ft.Column(
                            controls=[rating_dropdown, review_input, submit_button],
                            spacing=15,
                        ),

                        margin=ft.margin.only(top=15),
                        shape=ft.RoundedRectangleBorder(radius=15),
                        elevation=3
                    )
                )
            else:
                review_controls.append(
                    ft.Text("🔒 برای ثبت نظر لطفا وارد حساب کاربری شوید.", color=ft.Colors.GREY_600)
                )

            # ------------------ دکمه بازگشت ------------------
            back_button = ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                tooltip="بازگشت",
                on_click=lambda _: page.go("/"),
                icon_color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
            )

            # ------------------ اضافه کردن همه اجزا ------------------
            view.controls.extend([
                header,
                ft.Column(
                    controls=[price_row, countdown_control,add_to_cart_button],
                    alignment=ft.CrossAxisAlignment.END
                ),
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(content=image_control, padding=10, col={"sm": 12, "md": 6}),
                        ft.Container(content=ft.Column([desc_row]), padding=10, col={"sm": 12, "md": 6}),
                    ],
                    spacing=10,
                    run_spacing=20
                ),
                ft.Column(controls=specs_controls, spacing=5, horizontal_alignment=ft.CrossAxisAlignment.END),
                ft.Container(content=ft.Column(controls=review_controls, spacing=10),
                             padding=10,
                             border=ft.border.all(1, ft.Colors.GREY_300),
                             border_radius=8),
                ft.Row([back_button], alignment=ft.MainAxisAlignment.END),
            ])

            # توقف تایمر هنگام خروج
            def on_dispose(e):
                if countdown_timer:
                    countdown_timer.stop()
            view.on_dispose = on_dispose

        except Exception as e:
            view.controls.append(ft.Text(f"❌ خطا در دریافت جزئیات: {e}", color=ft.Colors.RED))

        return view

    return build_view()
