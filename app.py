import tkinter as tk
from tkinter import messagebox as msg
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

    def _program_exit(self) -> None:
        if msg.askyesno("Exit?", "Are you sure you want to exit?"):
            self.destroy()
