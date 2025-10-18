import flet as ft
import asyncio

class CountdownTimer:
    def __init__(self, seconds: int, on_finish=None):
        self.total_seconds = seconds
        self.seconds_left = seconds
        self.on_finish = on_finish
        self.running = False
        self.page = None
        self.task = None

        self.timer_text = ft.Text(
            "", size=18, color=ft.Colors.ORANGE_700, weight=ft.FontWeight.BOLD
        )

    def get_control(self):
        return self.timer_text

    async def _run_timer(self):
        try:
            while self.running and self.seconds_left > 0:
                if not self.page:
                    break

                hours = self.seconds_left // 3600
                minutes = (self.seconds_left % 3600) // 60
                seconds = self.seconds_left % 60
                self.timer_text.value = f"⏳ زمان باقی‌مانده: {hours:02}:{minutes:02}:{seconds:02}"

                # ✅ فقط یکبار کل صفحه آپدیت بشه (نه کنترل جدا)
                self.page.update()

                await asyncio.sleep(1)
                self.seconds_left -= 1

            if self.running and self.seconds_left <= 0:
                if self.page:
                    if self.timer_text in self.page.controls:
                        self.page.controls.remove(self.timer_text)
                    self.page.update()
                if self.on_finish:
                    self.on_finish()
        except asyncio.CancelledError:
            pass

    def start(self, page: ft.Page):
        if not self.running:
            self.running = True
            self.page = page
            if self.timer_text not in page.controls:
                page.add(self.timer_text)
            self.task = page.run_task(self._run_timer)

    def stop(self):
        self.running = False
        if self.task:
            try:
                self.task.cancel()
            except Exception:
                pass

    def reset(self):
        self.seconds_left = self.total_seconds
        if self.page:
            hours = self.total_seconds // 3600
            minutes = (self.total_seconds % 3600) // 60
            seconds = self.total_seconds % 60
            self.timer_text.value = f"⏳ زمان باقی‌مانده : {hours:02}:{minutes:02}:{seconds:02}"
            self.page.update()
