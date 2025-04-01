import tkinter as tk
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
        # Window config
        self.title("CryptoService")
        self.config(padx=50, pady=100)
        self.resizable(False, False)
        # Page container
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        # Frames dict
        self.frames = {}
        self.show_frame("MainPage")

    def show_frame(self, page_name: str) -> tk.Frame:
        if page_name not in self.frames:
            page_class = self.pages[page_name]
            frame = page_class(self.container, self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        frame = self.frames[page_name]
        frame.tkraise()
        return frame
