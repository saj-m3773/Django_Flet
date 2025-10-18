import flet as ft
import requests

from get_base64_image import get_base64_image

API_CATEGORIES = "http://127.0.0.1:8000/api/categories/"

def get_parent_categories():
    try:
        res = requests.get(API_CATEGORIES)
        res.raise_for_status()
        return res.json()
    except:
        return []

def category_card(cat, page: ft.Page):
    # کارت ساده دسته‌بندی
    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(cat["name"], weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            padding=10,
        ),
        elevation=2,
        margin=ft.margin.all(4),
    )
