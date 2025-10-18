# navigation.py
import flet as ft

class Navigator:
    def __init__(self, page: ft.Page):
        self.page = page
        self.history = []
        self.forward_stack = []

    def go_to(self, route: str):
        """رفتن به صفحه جدید و ریست کردن جلو"""
        self.history.append(self.page.route)
        self.forward_stack = []
        self.page.go(route)

    def go_back(self, e=None):
        """رفتن به صفحه قبلی"""
        if self.history:
            last = self.history.pop()
            self.forward_stack.append(self.page.route)
            self.page.go(last)

    def go_forward(self, e=None):
        """رفتن به صفحه جلو"""
        if self.forward_stack:
            next_route = self.forward_stack.pop()
            self.history.append(self.page.route)
            self.page.go(next_route)
