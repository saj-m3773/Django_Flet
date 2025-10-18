import flet as ft

from Account.user_profile_view import get_profile_view
from Order.checkout_view import get_checkout_view
from Order.orders_view import get_orders_view
from Order.payment_result_view import get_payment_result_view
from Product.Product_list import get_product_list_view
from Product.Prpduct_detail import get_product_detail_view
from Product.get_review_submit_view import get_review_submit_view
from Account.user_register import get_register_view
from Account.login_view import get_login_view
from Account.reset_password import reset_password_view
from Account.forgot_password import  forgot_password_view
from Account.dashboard import get_dashboard_view
from Account.edet_profile_view import   get_edit_profile_view
from Order.cart_view import get_cart_view
from Product.categories_view import get_category_view


# ---------------- مدیریت مسیرها ----------------
def route_change(e: ft.RouteChangeEvent):
    page = e.page
    page.views.clear()

    # ---------------- صفحه اصلی ----------------
    if e.route == "/":
        page.views.append(get_product_list_view(page))

    # ---------------- ارسال نظر ----------------
    elif e.route.startswith("/product/") and "/review" in e.route:
        product_id = e.route.split("/product/")[1].split("/review")[0]
        token = page.client_storage.get("access_token")
        if not token:
            page.go("/login")
            return
        page.views.append(get_review_submit_view(page, product_id, token))

    # ---------------- جزئیات محصول ----------------
    elif e.route.startswith("/product/"):
        product_id = e.route.split("/product/")[1]
        page.views.append(get_product_detail_view(page, product_id))

    # ---------------- ثبت‌نام ----------------
    elif e.route == "/register":
        page.views.append(get_register_view(page))

    # ---------------- ورود ----------------
    elif e.route == "/login":
        page.views.append(get_login_view(page))

    # ---------------- فراموشی رمز عبور ----------------
    elif e.route == "/forgot-password":
        page.views.append(forgot_password_view(page))

    elif e.route.startswith("/reset-password/"):
        token = e.route.split("/reset-password/")[1]
        page.views.append(reset_password_view(page, token))

    # ---------------- داشبورد ----------------
    elif e.route == "/dashboard":
        page.views.append(get_dashboard_view(page, ))
    elif e.route == "/dashboard":
        token = page.client_storage.get("access_token")
        if not token:
            page.go("/login")
            return
        page.views.append(get_dashboard_view(page))

    elif e.route == "/dashboard/profile":
        token = page.client_storage.get("access_token")
        if not token:
            page.go("/login")
            return
        page.views.append(get_profile_view(page, token))

    elif e.route == "/dashboard/edit-profile":
        token = page.client_storage.get("access_token")
        if not token:
            page.go("/login")
            return
        page.views.append(get_edit_profile_view(page, page))  # 👈 nav = page

    # ---------------- سبد خرید ----------------
    elif e.route == "/cart":
        token = page.client_storage.get("access_token")
        if not token:
            page.go("/login")
            return
        page.views.append(get_cart_view(page))
    elif e.route == "/checkout":
        page.views.append(get_checkout_view(page))
    elif e.route == "/orders":
        page.views.append(get_orders_view(page))

    # ---------------- مسیر بازگشت از درگاه ----------------
    elif e.route.startswith("/payment-result"):
        # فرض: آدرس بازگشت از درگاه شبیه زیر است:
        # /payment-result?Authority=XYZ123&Status=OK
        query_params = dict(param.split("=") for param in e.route.split("?")[1].split("&"))
        authority = query_params.get("Authority")
        status = query_params.get("Status")
        page.views.append(get_payment_result_view(page, authority, status))

    # ---------------- دسته‌بندی‌ها ----------------
    elif e.route == "/categories":
        page.views.append(get_category_view(page))

    elif e.route.startswith("/category/"):
        slug = e.route.split("/category/")[1]
        page.views.append(get_category_view(page, slug=slug))

    # ---------------- مسیر پیش‌فرض (404) ----------------
    else:
        page.views.append(
            ft.View("/", [ft.Text("⛔ صفحه مورد نظر یافت نشد", color="red")])
        )

    page.update()


# ---------------- نقطه شروع برنامه ----------------
def main(page: ft.Page):
    page.title = "🛒 فروشگاه آنلاین"
    page.on_route_change = route_change
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main)
