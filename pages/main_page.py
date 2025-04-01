import tkinter as tk
from tkinter import ttk, messagebox as msg
from typing import TYPE_CHECKING
from .base_page import BasePage
from .config_vars import MAIN_PAGE_SEARCH_DELAY_MS, MAIN_PAGE_SEARCH_FIELD_PH

if TYPE_CHECKING:
    from app import MyApp
    from .crypto_markets import CryptoMarkets


class MainPage(BasePage):

    def __init__(self, parent: tk.Frame, controller: "MyApp") -> None:
        super().__init__(parent, controller, {"columns": [], "show": ""})
        # Bind double click event for tree
        self._tree.bind("<Double-1>", self._on_tree_row_dbl_click)
        # Data field
        self._df = None
        # Search field
        self._search_entry = ttk.Entry(self)
        self._search_entry.bind("<FocusIn>", lambda _: self._search_entry_focus_in())
        self._search_entry.bind("<FocusOut>", lambda _: self._search_entry_focus_out())
        self._search_entry.bind("<KeyRelease>", self._plan_treeview_filtering)
        self._search_timer = None
        # Forward button
        self._forward_button = tk.Button(self, text="Forward >",
                                         command=lambda: self._controller.show_frame("CryptoMarkets"), state="disabled")
        # Frame setup
        self._place_widgets()
        self._refresh()

    def _place_widgets(self) -> None:
        self._search_entry.grid(row=0, column=0)
        self._forward_button.grid(row=0, column=1)
        self._tree.grid(row=1, column=0, columnspan=2)
        self._scrollbar.grid(row=1, column=2, sticky="ns")

    def _update_page(self) -> None:
        self._df = self._controller.service.get_asset_price()# n_rows=2000)
        self._filter_treeview()
        self._search_entry_focus_out()

    def _on_tree_row_dbl_click(self, event: tk.Event) -> None:
        row_id = self._tree.identify_row(event.y)
        if row_id:
            self._tree.selection_set(row_id)
            crypto_markets_page: CryptoMarkets = self._controller.show_frame("CryptoMarkets")
            crypto_markets_page.set_asset(asset_id=row_id)
            self._forward_button.configure(state="normal")

    def _search_entry_focus_in(self) -> None:
        if self._search_entry.get() == MAIN_PAGE_SEARCH_FIELD_PH:
            self._search_entry.delete(0, tk.END)
            self._search_entry.configure(foreground="black")

    def _search_entry_focus_out(self) -> None:
        if self._search_entry.get() == "":
            self._search_entry.insert(0, MAIN_PAGE_SEARCH_FIELD_PH)
            self._search_entry.configure(foreground="gray")

    def _plan_treeview_filtering(self, event: tk.Event = None) -> None:
        if self._search_timer:
            self.after_cancel(self._search_timer)
        self._search_timer = self.after(MAIN_PAGE_SEARCH_DELAY_MS, self._filter_treeview, event)

    def _filter_treeview(self, event: tk.Event = None) -> None:
        search_text = "" if self._search_entry.get() == MAIN_PAGE_SEARCH_FIELD_PH else self._search_entry.get().strip()
        mask = self._df.astype(str).apply(lambda col: col.str.contains(search_text, case=False))
        filtered_df = self._df[mask.any(axis=1)]
        self._fill_treeview(filtered_df)
        if filtered_df.empty and event and event.char.isalnum():
            msg.showinfo("Search Result", "Nothing was found for your request!")
