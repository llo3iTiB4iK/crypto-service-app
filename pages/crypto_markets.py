import tkinter as tk
from tkinter import ttk
import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app import MyApp

DATA_REFRESH_TIME_SEC = 60


class CryptoMarkets(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: "MyApp") -> None:
        super().__init__(parent)
        self.controller = controller
        self._refresh_task = None
        # Back button
        self.back_button = tk.Button(self, text="< Back", command=self._go_back)
        # Treeview for data
        self.tree = ttk.Treeview(self, columns=[], show="headings")
        # Scrollbar for treeview
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        # Setup frame
        self._place_widgets()

    def _place_widgets(self) -> None:
        self.back_button.grid(row=0, column=0)
        self.tree.grid(row=1, column=0)
        self.scrollbar.grid(row=1, column=1, sticky="ns")

    def update_crypto_markets(self, id_: str) -> None:
        data = self.controller.service.get_crypto_markets(asset_id=id_)
        self._fill_treeview(data)
        self.after(DATA_REFRESH_TIME_SEC * 1000, lambda: self.update_crypto_markets(id_))

    def _fill_treeview(self, data: pd.DataFrame) -> None:
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(data.columns)
        for col in data.columns:
            self.tree.heading(col, text=col)
        for index, row in data.iterrows():
            if index:
                self.tree.insert("", "end", iid=str(index), values=row.tolist())

    def _go_back(self) -> None:
        if self._refresh_task:
            self.after_cancel(self._refresh_task)
        self.controller.show_frame("MainPage")
