import tkinter as tk
from tkinter import ttk
import pandas as pd
from abc import ABC, abstractmethod
from .config_vars import PAGE_REFRESH_TIME_SEC
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from app import MyApp


class BasePage(tk.Frame, ABC):

    def __init__(self, parent: tk.Frame, controller: "MyApp", treeview_params: dict) -> None:
        super().__init__(parent)
        self._controller = controller
        self._page_refresh_timer = None
        self._delayed_tasks = {}
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
