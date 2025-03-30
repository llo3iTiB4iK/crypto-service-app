import tkinter as tk
from tkinter import ttk, messagebox as msg
import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app import MyApp
    from pages import CryptoMarkets

SEARCH_ENTRY_PLACEHOLDER = "Search by Name or Symbol..."
DATA_REFRESH_TIME_SEC = 60


class MainPage(tk.Frame):

    def __init__(self, parent: tk.Frame, controller: "MyApp") -> None:
        super().__init__(parent)
        self.controller = controller
        # Data field
        self.df = None
        # Search field
        self.search_entry = ttk.Entry(self)
        self.search_entry.bind("<FocusIn>", lambda _: self._search_entry_focus_in())
        self.search_entry.bind("<FocusOut>", lambda _: self._search_entry_focus_out())
        self.search_entry.bind("<KeyRelease>", lambda _: self._filter_treeview())
        # Treeview for data
        self.tree = ttk.Treeview(self, columns=[], show="")
        self.tree.bind("<Double-1>", self._on_row_dbl_click)
        # Scrollbar for treeview
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        # Frame setup
        self._place_widgets()
        self._reset_all()

    def _place_widgets(self) -> None:
        self.search_entry.grid(row=0, column=0, columnspan=2)
        self.tree.grid(row=1, column=0)
        self.scrollbar.grid(row=1, column=1, sticky="ns")

    def _reset_all(self) -> None:
        self.df = self.controller.service.get_asset_price(n_rows=2000)
        self._filter_treeview()
        self._search_entry_focus_out()
        self.after(DATA_REFRESH_TIME_SEC * 1000, self._reset_all)

    def _search_entry_focus_in(self) -> None:
        if self.search_entry.get() == SEARCH_ENTRY_PLACEHOLDER:
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(foreground="black")

    def _search_entry_focus_out(self) -> None:
        if self.search_entry.get() == "":
            self.search_entry.insert(0, SEARCH_ENTRY_PLACEHOLDER)
            self.search_entry.configure(foreground="gray")

    def _on_row_dbl_click(self, event: tk.Event) -> None:
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            markets_frame: CryptoMarkets = self.controller.show_frame("CryptoMarkets")
            markets_frame.update_crypto_markets(row_id)

    def _fill_treeview(self, data: pd.DataFrame) -> None:
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(data.columns)
        for index, row in data.iterrows():
            if index:
                self.tree.insert("", "end", iid=str(index), values=row.tolist())

    def _filter_treeview(self) -> None:
        search_text = "" if self.search_entry.get() == SEARCH_ENTRY_PLACEHOLDER else self.search_entry.get().strip()
        filtered_df = self.df[self.df.apply(lambda row: row.astype(str).str.contains(search_text, case=False).any(), axis=1)]
        self._fill_treeview(filtered_df)
        if filtered_df.empty:
            msg.showinfo("Search Result", "Nothing was found for your request!")
