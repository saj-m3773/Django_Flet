import flet as ft
from shared.appbar import shared_appbar

def get_dashboard_view(page: ft.Page):
    token = page.session.get("access")  # گرفتن توکن از session
    if not token:
        page.go("/login")
        page.update()
        return

    # --- منوی کناری داشبورد ---
    nav_items = [
        {"label": "پروفایل", "icon": ft.Icons.PERSON, "route": "/dashboard/profile"},
        {"label": "سفارش‌ها", "icon": ft.Icons.SHOPPING_BAG, "route": "/dashboard/orders"},
        {"label": "علاقه‌مندی‌ها", "icon": ft.Icons.FAVORITE, "route": "/dashboard/favorites"},
        {"label": "تنظیمات", "icon": ft.Icons.SETTINGS, "route": "/dashboard/settings"},
        {"label": "خروج", "icon": ft.Icons.LOGOUT, "route": "/login"},
    ]

    sidebar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=[
            ft.NavigationRailDestination(icon=item["icon"], label=item["label"])
            for item in nav_items
        ],
        on_change=lambda e: page.go(nav_items[e.control.selected_index]["route"]),
    )

    # --- محتوای بخش‌های مختلف ---
    content = ft.Container(
        expand=True,
        content=ft.Column(
            [
                ft.Text("به داشبورد خوش آمدید 🎉", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("اینجا اطلاعات کاربری و سفارشاتت نمایش داده میشه.")
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=20
        ),
        padding=20,
    )

    # --- View کامل ---
    return ft.View(
        route="/dashboard",
        controls=[
            shared_appbar(page),  # AppBar داینامیک
            ft.Row(
                [
                    sidebar,
                    ft.VerticalDivider(width=1),
                    content
                ],
                expand=True
            )
        ]
    )
