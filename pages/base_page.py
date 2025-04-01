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
        self.controller = controller
        self._page_refresh_timer = None
        # Treeview for data table
        self.tree = ttk.Treeview(self, **treeview_params)
        # Scrollbar for treeview table
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

    @abstractmethod
    def place_widgets(self) -> None:
        pass

    @abstractmethod
    def update_page(self) -> None:
        pass

    def refresh(self) -> None:
        self.update_page()
        self._page_refresh_timer = self.after(PAGE_REFRESH_TIME_SEC * 1000, self.refresh)

    def stop_refreshing(self):
        if self._page_refresh_timer:
            self.after_cancel(self._page_refresh_timer)
            self._page_refresh_timer = None

    def fill_treeview(self, data: pd.DataFrame) -> None:
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(data.columns)
        for col in data.columns:
            self.tree.heading(col, text=col)
        for index, row in data.iterrows():
            if index:
                self.tree.insert("", "end", iid=index, values=row.tolist())

    @staticmethod
    def plot_data(data: pd.DataFrame | pd.Series, figure: Figure, **plot_kwargs: Any) -> plt.Axes:
        figure.clear()
        ax = figure.add_subplot()
        data.plot(ax=ax, **plot_kwargs)
        return ax
