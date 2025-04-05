import tkinter as tk
from tkinter import ttk, messagebox as msg
from ttkthemes import ThemedTk
import os
import json
from pages import MainPage, CryptoMarkets
from crypto_service import CryptoService
from config import APP_TITLE, ICON_PATH, USER_CONFIG


class MyApp(ThemedTk):
    pages = {
        "MainPage": MainPage,
        "CryptoMarkets": CryptoMarkets
    }

    def __init__(self) -> None:
        super().__init__()
        self.service = CryptoService()
        self.conversion_rates = self.service.get_conversion_rates()
        settings = self._load_settings()
        # Global variable for currency choice
        self.selected_currency = tk.StringVar(value=settings.get("currency", self.conversion_rates.index[0]))
        self.selected_currency.trace_add('write', lambda *args: self._on_currency_change())
        self._on_currency_change()
        # Global variable for theme choice
        self.selected_theme = tk.StringVar(value=settings.get("theme", "default"))
        self.selected_theme.trace_add('write', lambda *args: self._on_theme_change())
        self._on_theme_change()
        # Window config
        self.iconbitmap(default=ICON_PATH)
        self.title(APP_TITLE)
        self.resizable(False, False)
        # Page container
        self._container = ttk.Frame(self, padding=50)
        self._container.pack(side="top", fill="both", expand=True)
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_columnconfigure(0, weight=1)
        # Frames dict
        self._frames = {}
        self.show_frame("MainPage")
        # Custom program exit
        self.bind("<Escape>", lambda _: self.iconify())
        self.protocol("WM_DELETE_WINDOW", self._program_exit)

    @staticmethod
    def _load_settings() -> dict:
        if os.path.exists(USER_CONFIG):
            with open(USER_CONFIG) as f:
                return json.load(f)
        return {}

    def _save_settings(self) -> None:
        settings = {
            "currency": self.selected_currency.get(),
            "theme": self.selected_theme.get(),
        }
        with open(USER_CONFIG, "w") as f:
            json.dump(settings, f)

    def _on_currency_change(self) -> None:
        new_currency = self.selected_currency.get()
        self.service.conversion_rate = self.conversion_rates[new_currency]
        if hasattr(self, "_frames"):
            for frame in self._frames.values():
                frame.force_update()

    def _on_theme_change(self) -> None:
        new_theme = self.selected_theme.get()
        self.set_theme(new_theme)

    def show_frame(self, page_name: str) -> ttk.Frame:
        if page_name not in self._frames:
            page_class = self.pages[page_name]
            frame = page_class(self._container, self)
            self._frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        frame = self._frames[page_name]
        frame.tkraise()
        return frame

    def _program_exit(self) -> None:
        if msg.askyesno("Exit?", "Are you sure you want to exit?"):
            self._save_settings()
            self.destroy()
