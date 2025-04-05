import tkinter as tk
from tkinter import ttk
import pandas as pd
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable
from config import PAGE_REFRESH_TIME_SEC

if TYPE_CHECKING:
    from app import MyApp


class BasePage(ttk.Frame, ABC):

    def __init__(self, parent: ttk.Frame, controller: "MyApp", treeview_params: dict) -> None:
        super().__init__(parent)
        self._controller = controller
        self._page_refresh_timer = None
        self._delayed_tasks = {}
        # Combobox for currency choice
        self._currency_selector = ttk.Combobox(self, state="readonly", textvariable=self._controller.selected_currency,
                                               values=self._controller.conversion_rates.index.sort_values().tolist())
        # Combobox for theme choice
        self._theme_selector = ttk.Combobox(self, state="readonly", textvariable=self._controller.selected_theme,
                                            values=sorted(self._controller.get_themes()))
        # Fix frozen selection bug
        def clear_combobox_selection(e: tk.Event) -> None: e.widget.selection_clear()
        self._currency_selector.bind("<<ComboboxSelected>>", clear_combobox_selection)
        self._theme_selector.bind("<<ComboboxSelected>>", clear_combobox_selection, add="+")
        # Treeview for data table
        self._tree = ttk.Treeview(self, **treeview_params)
        # Scrollbar for treeview table
        self._scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=self._scrollbar.set)

    @abstractmethod
    def _place_widgets(self) -> None:
        pass

    @abstractmethod
    def _update_page(self) -> None:
        pass

    def _start_refreshing(self, save_selection: bool = True) -> None:
        selection_buffer = self._tree.selection()
        self._update_page()
        if save_selection:
            self._tree.selection_set(selection_buffer)
        self._page_refresh_timer = self.after(PAGE_REFRESH_TIME_SEC * 1000, self._start_refreshing)

    def _stop_refreshing(self) -> None:
        if self._page_refresh_timer:
            self.after_cancel(self._page_refresh_timer)
            self._page_refresh_timer = None

    def _schedule_delayed_task(self, task_name: str, delay: int, callback: Callable, *args: Any) -> None:
        if task_name in self._delayed_tasks:
            self.after_cancel(self._delayed_tasks[task_name])
        self._delayed_tasks[task_name] = self.after(delay, callback, *args)

    def _fill_treeview(self, data: pd.DataFrame) -> None:
        self._tree.delete(*self._tree.get_children())
        self._tree["columns"] = list(data.columns)
        for col in data.columns:
            self._tree.heading(col, text=col)
        for index, row in data.iterrows():
            if index:
                self._tree.insert("", "end", iid=index, values=row.tolist())

    def force_update(self) -> None:
        self._stop_refreshing()
        self._update_page()
        self._start_refreshing()
