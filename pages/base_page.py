import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import pandas as pd
from matplotlib.figure import Figure
from abc import ABC, abstractmethod
from .config_vars import PAGE_REFRESH_TIME_SEC
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app import MyApp


class BasePage(tk.Frame, ABC):

    def __init__(self, parent: tk.Frame, controller: "MyApp", treeview_params: dict) -> None:
        super().__init__(parent)
        self._controller = controller
        self._page_refresh_timer = None
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

    def _refresh(self) -> None:
        self._update_page()
        self._page_refresh_timer = self.after(PAGE_REFRESH_TIME_SEC * 1000, self._refresh)

    def _stop_refreshing(self) -> None:
        if self._page_refresh_timer:
            self.after_cancel(self._page_refresh_timer)
            self._page_refresh_timer = None

    def _fill_treeview(self, data: pd.DataFrame) -> None:
        selection_buffer = self._tree.selection()
        self._tree.delete(*self._tree.get_children())
        self._tree["columns"] = list(data.columns)
        for col in data.columns:
            self._tree.heading(col, text=col)
        for index, row in data.iterrows():
            if index:
                self._tree.insert("", "end", iid=index, values=row.tolist())
        self._tree.selection_set(selection_buffer)

    @staticmethod
    def _plot_data(data: pd.DataFrame | pd.Series, figure: Figure, **plot_kwargs: Any) -> plt.Axes:
        figure.clear()
        ax = figure.add_subplot()
        data.plot(ax=ax, **plot_kwargs)
        return ax
