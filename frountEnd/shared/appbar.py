import flet as ft


def shared_appbar(page: ft.Page) -> ft.AppBar:
    """AppBar مشترک بین صفحات"""

    # ---------------- تغییر تم ----------------
    theme_icon = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE,
        tooltip="تغییر تم"
    )

    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_icon.icon = ft.Icons.DARK_MODE
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_icon.icon = ft.Icons.LIGHT_MODE
        page.update()

    theme_icon.on_click = toggle_theme

    # ---------------- بررسی وضعیت ورود ----------------
    is_logged_in = page.session.get("access") is not None

    if is_logged_in:
        # وقتی کاربر لاگین کرده
        actions = [
            ft.IconButton(
                icon=ft.Icons.HOME,
                tooltip="خانه",
                on_click=lambda e: page.go("/")
            ),
            ft.IconButton(
                icon=ft.Icons.DASHBOARD,
                tooltip="پنل کاربری",
                on_click=lambda e: page.go("/dashboard")
            ),
            ft.IconButton(
                icon=ft.Icons.SHOPPING_CART,
                tooltip="سبد خرید",
                on_click=lambda e: page.go("/cart")
            ),
            ft.IconButton(
                icon=ft.Icons.LOGOUT,
                tooltip="خروج",
                on_click=lambda e: logout_user(page)
            ),
            theme_icon
        ]
    else:
        # وقتی کاربر لاگین نکرده
        actions = [
            ft.IconButton(
                icon=ft.Icons.PERSON_ADD,
                tooltip="ثبت‌نام",
                on_click=lambda e: page.go("/register")
            ),
            ft.IconButton(
                icon=ft.Icons.LOGIN,
                tooltip="ورود",
                on_click=lambda e: page.go("/login")
            ),
            ft.IconButton(
                icon=ft.Icons.LOCK_RESET,
                tooltip="فراموشی رمز عبور",
                on_click=lambda e: page.go("/forgot-password")
            ),
            theme_icon
        ]

    # ---------------- بازگرداندن AppBar ----------------
    return ft.AppBar(
        title=ft.Text("فروشگاه من", style=ft.TextThemeStyle.TITLE_LARGE),
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        actions=actions
    )


# ---------------- تابع خروج ----------------
def logout_user(page: ft.Page):
    """پاک کردن نشست کاربر و هدایت به صفحه اصلی"""
    page.session.clear()
    page.go("/")
    page.update()
