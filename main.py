# -*- coding: utf-8 -*-
"""
AI & Финансы — мобильное приложение на Flet с русскоязычным интерфейсом.
"""

import flet as ft
from core.fetchers import get_exchange_rates, get_market_indices, get_ai_leaderboard
from core.market_fallback import FALLBACK_RATES, FALLBACK_INDICES

ACCENT = "#3D5AFE"
POSITIVE = "#00C853"
NEGATIVE = "#D50000"

CATEGORY_ORDER = ["video", "image", "audio", "text", "multimodal"]
CATEGORY_TITLES = {
    "video": "Видео",
    "image": "Изображения",
    "audio": "Аудио",
    "text": "Текст",
    "multimodal": "Мультимодальные"
}
CATEGORY_ICONS = {
    "video": ft.Icons.MOVIE_OUTLINED,
    "image": ft.Icons.IMAGE_OUTLINED,
    "audio": ft.Icons.AUDIOTRACK_OUTLINED,
    "text": ft.Icons.TEXT_FIELDS_OUTLINED,
    "multimodal": ft.Icons.HUB_OUTLINED
}
CATEGORY_HINTS = {
    "video": "Бенчмарки генерации видео (качество движения, физика, детализация)",
    "image": "Рейтинги генераторов изображений (фотореализм, промпт-адгеренция)",
    "audio": "Качество синтеза речи, клонирования голоса и музыкальных моделей",
    "text": "Производительность языковых моделей (LLM) в логике, коде и рассуждениях",
    "multimodal": "Интегрированные модели понимания текста, визуальных данных и звука"
}

class AIFinanceApp:
    def __init__(self):
        self.nav_index = 0
        self.category = "video"
        self.search_query = ""
        
        self.rates_data = []
        self.indices_data = []
        self.leaderboard_data = {}
        self.market_note = "Загрузка данных рынка..."
        self.ai_note = "Загрузка рейтингов AI..."
        self.is_offline = False

        self.content_area = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self.status_banner = ft.Container(
            visible=False,
            padding=8,
            bgcolor=ft.Colors.AMBER_100,
            border_radius=8,
            content=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=16, color=ft.Colors.AMBER_900),
                ft.Text("", size=12, color=ft.Colors.AMBER_900, expand=True)
            ])
        )
        # Убран устаревший border_radius, заменен на padding/внутреннюю структуру
        self.search_field = ft.TextField(
            hint_text="Поиск...",
            prefix_icon=ft.Icons.SEARCH,
            dense=True,
            text_size=13,
            on_change=self.on_search_change,
            visible=False
        )
        self.chips_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8)

    def load_data(self):
        rates, r_ok = get_exchange_rates()
        indices, i_ok = get_market_indices()
        self.rates_data = rates
        self.indices_data = indices

        if not r_ok and not i_ok:
            self.is_offline = True
            self.market_note = "Офлайн-режим: показаны резервные котировки."
        else:
            self.is_offline = False
            self.market_note = "Данные обновлены в реальном времени (ЦБ РФ / биржи)."

        lb, lb_ok = get_ai_leaderboard()
        self.leaderboard_data = lb
        if not lb_ok:
            self.ai_note = "Загружен локальный снимок бенчмарков AI."
        else:
            self.ai_note = "Актуальные рейтинги AI-моделей."

        self.update_view()

    def build(self, page: ft.Page):
        self.page = page
        page.title = "AI & Финансы"
        page.theme_mode = ft.ThemeMode.SYSTEM
        page.padding = 0
        page.bgcolor = ft.Colors.GREY_50

        self.app_bar = ft.AppBar(
            title=ft.Text("AI & Финансы", weight="w700", size=18),
            center_title=False,
            bgcolor=ft.Colors.SURFACE,
            actions=[
                ft.IconButton(icon=ft.Icons.SEARCH, tooltip="Поиск", on_click=lambda e: self.toggle_search()),
                ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Обновить", on_click=lambda e: self.on_refresh(e))
            ]
        )

        self.nav_bar = ft.NavigationBar(
            selected_index=0,
            on_change=self.on_nav_change,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.MONETIZATION_ON_OUTLINED, selected_icon=ft.Icons.MONETIZATION_ON, label="Финансы"),
                ft.NavigationBarDestination(icon=ft.Icons.LEADERBOARD_OUTLINED, selected_icon=ft.Icons.LEADERBOARD, label="AI-рейтинг"),
                ft.NavigationBarDestination(icon=ft.Icons.INFO_OUTLINE, selected_icon=ft.Icons.INFO, label="О программе"),
            ]
        )

        main_layout = ft.Column([
            self.app_bar,
            self.search_field,
            self.status_banner,
            self.content_area
        ], expand=True, spacing=0)

        page.add(ft.SafeArea(content=main_layout, expand=True))
        page.navigation_bar = self.nav_bar
        
        self.load_data()

    def toggle_search(self):
        self.search_field.visible = not self.search_field.visible
        if not self.search_field.visible:
            self.search_query = ""
            self.search_field.value = ""
        self.page.update()
        self.update_view()

    def on_search_change(self, e):
        self.search_query = e.control.value.strip().lower()
        self.update_view()

    def on_nav_change(self, e):
        self.nav_index = e.control.selected_index
        self.search_field.visible = False
        self.search_query = ""
        self.search_field.value = ""
        self.update_view()

    def on_refresh(self, e):
        self.load_data()
        self.page.snack_bar = ft.SnackBar(ft.Text("Данные обновлены!"))
        self.page.snack_bar.open = True
        self.page.update()

    def on_category(self, cat):
        self.category = cat
        self.update_view()

    def update_view(self):
        if not hasattr(self, 'page') or self.page is None:
            return
            
        self.content_area.controls.clear()

        if self.is_offline or self.nav_index == 0:
            self.status_banner.visible = True
            self.status_banner.content.controls[1].value = self.market_note
        elif self.nav_index == 1:
            self.status_banner.visible = True
            self.status_banner.content.controls[1].value = self.ai_note
        else:
            self.status_banner.visible = False

        self.content_area.controls.append(self.status_banner)

        if self.nav_index == 0:
            self.build_finance_view()
        elif self.nav_index == 1:
            self.build_ai_view()
        elif self.nav_index == 2:
            self.build_about_view()

        self.content_area.update()
        self.page.update()

    def build_finance_view(self):
        rates = self.rates_data
        indices = self.indices_data

        if self.search_query:
            rates = [r for r in rates if self.search_query in r.get("name", "").lower() or self.search_query in r.get("code", "").lower()]
            indices = [i for i in indices if self.search_query in i.get("name", "").lower()]

        self.content_area.controls.append(
            ft.Container(
                padding=12,  # Безопасный отступ числом
                content=ft.Text("Курсы валют ЦБ РФ", size=16, weight="w700")
            )
        )

        rates_cards = []
        for r in rates:
            diff = r.get("diff", 0.0)
            diff_color = POSITIVE if diff >= 0 else NEGATIVE
            diff_str = f"+{diff:.2f}%" if diff >= 0 else f"{diff:.2f}%"
            
            card = ft.Card(
                elevation=1,
                content=ft.Container(
                    padding=12,
                    content=ft.Row([
                        ft.Column([
                            ft.Text(r.get("code"), weight="w700", size=15),
                            ft.Text(r.get("name"), size=11, opacity=0.6)
                        ], expand=True),
                        ft.Column([
                            ft.Text(f"{r.get('value'):.2f} ₽", weight="w700", size=15, text_align="right"),
                            ft.Text(f"номинал {r.get('nominal')}", size=11, opacity=0.6, text_align="right")
                        ], alignment="center"),
                        ft.Container(width=10),
                        ft.Container(
                            padding=6,
                            border_radius=6,
                            bgcolor=ft.Colors.with_opacity(0.1, diff_color),
                            content=ft.Text(diff_str, color=diff_color, size=11, weight="w600")
                        )
                    ], alignment="spaceBetween")
                )
            )
            rates_cards.append(card)

        self.content_area.controls.append(
            ft.Container(
                padding=12,
                content=ft.Column(rates_cards, spacing=8)
            )
        )

        self.content_area.controls.append(
            ft.Container(
                padding=12,
                content=ft.Text("Мировые и российские индексы", size=16, weight="w700")
            )
        )

        indices_cards = []
        for ind in indices:
            val = ind.get("value", 0.0)
            chg = ind.get("change_pct", 0.0)
            chg_color = POSITIVE if chg >= 0 else NEGATIVE
            chg_str = f"+{chg:.2f}%" if chg >= 0 else f"{chg:.2f}%"

            card = ft.Card(
                elevation=1,
                content=ft.Container(
                    padding=12,
                    content=ft.Row([
                        ft.Column([
                            ft.Text(ind.get("name"), weight="w700", size=14),
                            ft.Text(ind.get("region", "Мир"), size=11, opacity=0.6)
                        ], expand=True),
                        ft.Column([
                            ft.Text(f"{val:,.2f}", weight="w700", size=14, text_align="right"),
                            ft.Text(chg_str, color=chg_color, size=11, weight="w600", text_align="right")
                        ], alignment="center")
                    ], alignment="spaceBetween")
                )
            )
            indices_cards.append(card)

        self.content_area.controls.append(
            ft.Container(
                padding=12,
                content=ft.Column(indices_cards, spacing=8)
            )
        )

    def build_ai_view(self):
        self.chips_row.controls.clear()
        for key in CATEGORY_ORDER:
            selected = key == self.category
            chip = ft.Container(
                padding=10,
                border_radius=20,
                bgcolor=ft.Colors.with_opacity(0.22 if selected else 0.08, ACCENT),
                ink=True,
                on_click=lambda e, k=key: self.on_category(k),
                content=ft.Row([
                    ft.Icon(CATEGORY_ICONS[key], size=15, color=ACCENT),
                    ft.Text(CATEGORY_TITLES[key], size=12.5, weight="w600" if selected else "w400", color=ACCENT),
                ], spacing=6, tight=True)
            )
            self.chips_row.controls.append(chip)

        self.content_area.controls.append(
            ft.Container(
                padding=12,
                content=ft.Column([
                    ft.Text("AI Leaderboard (Рейтинг моделей)", size=16, weight="w700"),
                    self.chips_row,
                    ft.Row([
                        ft.Icon(CATEGORY_ICONS[self.category], size=16, color=ACCENT),
                        ft.Text(CATEGORY_HINTS[self.category], size=12.5, opacity=0.7, expand=True),
                    ], spacing=8, vertical_alignment="center")
                ], spacing=14)
            )
        )

        models = self.leaderboard_data.get(self.category, [])
        if self.search_query:
            models = [m for m in models if self.search_query in m.get("name", "").lower() or self.search_query in m.get("developer", "").lower()]

        if not models:
            self.content_area.controls.append(
                ft.Container(
                    padding=40,
                    alignment=ft.alignment.center,
                    content=ft.Text("Модели не найдены", opacity=0.5)
                )
            )
            return

        max_score = max([m.get("score", 1.0) for m in models]) if models else 1.0

        model_cards = []
        for idx, m in enumerate(models, 1):
            score = m.get("score", 0.0)
            ratio = min(max(score / max_score if max_score > 0 else 0, 0.05), 1.0)

            medal = ""
            if idx == 1: medal = "🥇 "
            elif idx == 2: medal = "🥈 "
            elif idx == 3: medal = "🥉 "

            tags_row = ft.Row([
                ft.Container(
                    padding=6,
                    border_radius=4,
                    bgcolor=ft.Colors.with_opacity(0.1, ACCENT),
                    content=ft.Text(t, size=10, color=ACCENT, weight="w600")
                ) for t in m.get("tags", [])
            ], spacing=4, wrap=True)

            card = ft.Card(
                elevation=1,
                content=ft.Container(
                    padding=14,
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"{medal}#{idx}", weight="w700", size=13, color=ACCENT),
                            ft.Text(m.get("name"), weight="w700", size=15, expand=True),
                            ft.Text(f"{score:.1f}", weight="w700", size=15, color=ACCENT)
                        ], alignment="spaceBetween"),
                        ft.Row([
                            ft.Text(f"Разработчик: {m.get('developer')}", size=12, opacity=0.6),
                        ]),
                        tags_row,
                        ft.Container(height=4),
                        ft.ProgressBar(value=ratio, color=ACCENT, bgcolor=ft.Colors.with_opacity(0.1, ACCENT), height=6)
                    ], spacing=6)
                )
            )
            model_cards.append(card)

        self.content_area.controls.append(
            ft.Container(
                padding=12,
                content=ft.Column(model_cards, spacing=10)
            )
        )

    def build_about_view(self):
        self.content_area.controls.append(
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Text("О приложении", size=18, weight="w700"),
                    ft.Text("Мобильное приложение на Python и Flet, объединяющее финансовый трекинг и актуальные бенчмарки генеративных ИИ-моделей.", size=13, opacity=0.8),
                    ft.Divider(),
                    ft.Text("Источники данных:", weight="w700", size=14),
                    ft.Text("• Курсы валют: ЦБ РФ.", size=12, opacity=0.7),
                    ft.Text("• Индексы: МосБиржа ISS API и Stooq.", size=12, opacity=0.7),
                    ft.Text("• AI Leaderboard: Сводные бенчмарки.", size=12, opacity=0.7),
                    ft.Divider(),
                    ft.Text("Версия: 1.0.0", size=12, opacity=0.5),
                    ft.Text("Собрано с использованием Flet 1.0", size=12, opacity=0.5)
                ], spacing=12)
            )
        )

def main(page: ft.Page):
    app = AIFinanceApp()
    app.build(page)

ft.run(main)