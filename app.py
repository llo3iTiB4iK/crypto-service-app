import tkinter as tk
from tkinter import ttk, messagebox as msg
from pages import MainPage, CryptoMarkets
from crypto_service import CryptoService


class MyApp(tk.Tk):
    pages = {
        "MainPage": MainPage,
        "CryptoMarkets": CryptoMarkets
    }

    def __init__(self) -> None:
        super().__init__()
        self.service = CryptoService()
        self._conversion_rates = self.service.get_conversion_rates()
        self.selected_currency = tk.StringVar(value=self._conversion_rates.index[0])
        # Combobox for currency choice
        self._currency_selector = ttk.Combobox(self, state="readonly", textvariable=self.selected_currency,
                                               values=self._conversion_rates.index.sort_values().tolist())
        self._currency_selector.pack()
        self._currency_selector.bind("<<ComboboxSelected>>", lambda _: self._on_currency_change())
        # Window config
        self.iconbitmap(default='icon.ico')
        self.title("CryptoService")
        self.config(padx=50, pady=50)
        self.resizable(False, False)
        # Page container
        self._container = tk.Frame(self)
        self._container.pack(side="top", fill="both", expand=True)
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_columnconfigure(0, weight=1)
        # Frames dict
        self._frames = {}
        self.show_frame("MainPage")
        # Custom program exit
        self.bind("<Escape>", lambda _: self.iconify())
        self.protocol("WM_DELETE_WINDOW", self._program_exit)

    def show_frame(self, page_name: str) -> tk.Frame:
        if page_name not in self._frames:
            page_class = self.pages[page_name]
            frame = page_class(self._container, self)
            self._frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        frame = self._frames[page_name]
        frame.tkraise()
        return frame

    def _on_currency_change(self):
        self.service.conversion_rate = self._conversion_rates[self.selected_currency.get()]
        for frame in self._frames.values():
            frame.update_page()

    def _program_exit(self) -> None:
        if msg.askyesno("Exit?", "Are you sure you want to exit?"):
            self.destroy()
