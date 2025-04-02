import tkinter as tk
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.dates as mdates
import mplcursors
from typing import TYPE_CHECKING, Any
from .base_page import BasePage
from .config_vars import MARKETS_PAGE_PLOT_DELAY_MS

if TYPE_CHECKING:
    from app import MyApp


class CryptoMarkets(BasePage):
    def __init__(self, parent: tk.Frame, controller: "MyApp") -> None:
        super().__init__(parent, controller, {"columns": [], "show": "headings"})
        self._tree.bind("<<TreeviewSelect>>", lambda _: self._on_tree_selection_change())
        self._tree.bind("<Control-a>", lambda _: self._tree.selection_set(self._tree.get_children()))
        self._asset_id = None
        # Back button
        self._back_button = tk.Button(self, text="< Back", command=lambda: self._controller.show_frame("MainPage"))
        # Matplotlib Figure for price history
        self._figure = Figure(figsize=(12, 6), dpi=50)  # todo: adjust size
        (self._ax1, self._ax2) = self._figure.subplots(1, 2)
        self._canvas = FigureCanvasTkAgg(self._figure, master=self)
        # Toolbar for scaling/moving chart
        self._toolbar = NavigationToolbar2Tk(self._canvas, window=self, pack_toolbar=False)
        # Setup frame
        self._place_widgets()

    def _place_widgets(self) -> None:
        self._back_button.grid(row=0, column=0)
        self._tree.grid(row=1, column=0)
        self._scrollbar.grid(row=1, column=1, sticky="ns")
        self._toolbar.grid(row=2, column=0, columnspan=2, sticky="ew")
        self._canvas.get_tk_widget().grid(row=3, column=0, columnspan=2, sticky="nsew")

    def update_page(self) -> None:
        asset_markets = self._controller.service.get_crypto_markets(asset_id=self._asset_id)
        self._fill_treeview(asset_markets)
        self._plot_asset_history()

    def _on_tree_selection_change(self):
        self._schedule_delayed_task("plot_tree_selection", MARKETS_PAGE_PLOT_DELAY_MS, self._plot_trade_volume_chart)

    def set_asset(self, asset_id: str) -> None:
        self._stop_refreshing()
        self._asset_id = asset_id
        self._start_refreshing(save_selection=False)
        self._plot_trade_volume_chart()

    def _plot_chart(self, ax: Axes, data: pd.Series, **plot_kwargs: Any) -> None:
        ax.clear()
        data.plot(ax=ax, **plot_kwargs)
        self._canvas.draw()
        self._figure.tight_layout()
        self._toolbar.update()

    def _plot_asset_history(self) -> None:
        currency = self._controller.selected_currency.get()
        asset_history = self._controller.service.get_crypto_history(asset_id=self._asset_id)
        self._plot_chart(self._ax1, asset_history, xlabel="Date", ylabel=currency,
                         title=f"Price History for \"{self._asset_id}\"", grid=True)

        def format_price(price: float) -> str:
            return f"{price:.2e}" if price < 0.01 else f"{price:.2f}"

        cursor = mplcursors.cursor(self._ax1, hover=mplcursors.HoverMode.Transient)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            f"{format_price(sel.target[1])} {currency}  on {mdates.num2date(sel.target[0]).strftime('%Y-%m-%d')}"
        ))

    def _plot_trade_volume_chart(self) -> None:
        selected_items = self._tree.selection()
        if not selected_items:
            selected_items = self._tree.get_children()

        columns = self._tree["columns"]
        data = [self._tree.item(item, "values") for item in selected_items]
        df = pd.DataFrame(data, columns=columns)

        target_values = df["Volume (%)"].astype(float).values
        target_index = (df["Exchange (ID)"] + " | " + df["Base (Symbol)"] + "/" + df["Quote (Symbol)"]).values
        if len(selected_items) == len(df):
            threshold = 0.03 * target_values.sum()
            target_index = [name if value >= threshold else "Others" for name, value in zip(target_index, target_values)]

        market_shares = pd.Series(target_values, index=target_index).groupby(level=0).sum()
        self._plot_chart(self._ax2, market_shares, kind="pie", autopct="%.1f%%",
                         title=f"\"{self._asset_id}\" Trading Volume Share by Exchange and Pair")
