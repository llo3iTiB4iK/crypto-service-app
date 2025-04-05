from tkinter import ttk
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors
from typing import TYPE_CHECKING, Any
from .base_page import BasePage
from config import MARKETS_PAGE_PLOT_DELAY_MS
from utils import Formatter

if TYPE_CHECKING:
    from app import MyApp


class CryptoMarkets(BasePage):
    def __init__(self, parent: ttk.Frame, controller: "MyApp") -> None:
        super().__init__(parent, controller, {"columns": [], "show": "headings"})
        self._tree.bind("<<TreeviewSelect>>", lambda _: self._on_tree_selection_change())
        self._tree.bind("<Control-a>", lambda _: self._tree.selection_set(self._tree.get_children()))
        self._asset_id = None
        # Back button
        self._back_button = ttk.Button(self, text="< Back", command=lambda: self._controller.show_frame("MainPage"))
        # Matplotlib Figure for price history
        self._figure = Figure(figsize=(12, 6), dpi=50)
        (self._ax1, self._ax2) = self._figure.subplots(1, 2)
        self._canvas = FigureCanvasTkAgg(self._figure, master=self)
        # Handle theme choice for plots properly
        self._theme_selector.bind("<<ComboboxSelected>>", lambda _: self._on_theme_change(), add="+")
        self._fg_color = None
        self._update_canvas_colors()
        # Setup frame
        self._place_widgets()

    def _place_widgets(self) -> None:
        self._currency_selector.grid(row=0, column=0)
        self._theme_selector.grid(row=0, column=1)
        self._back_button.grid(row=1, column=1)
        self._tree.grid(row=2, column=0, columnspan=2)
        self._scrollbar.grid(row=2, column=2, sticky="ns")
        self._canvas.get_tk_widget().grid(row=3, column=0, columnspan=2, sticky="nsew")

    def _update_page(self) -> None:
        asset_markets = self._controller.service.get_crypto_markets(asset_id=self._asset_id)
        self._fill_treeview(asset_markets)
        self._plot_asset_history()

    def _on_tree_selection_change(self) -> None:
        self._schedule_delayed_task("plot_tree_selection", MARKETS_PAGE_PLOT_DELAY_MS, self._plot_trade_volume_chart)

    def set_asset(self, asset_id: str) -> None:
        self._stop_refreshing()
        self._asset_id = asset_id
        self._start_refreshing(save_selection=False)
        self._plot_trade_volume_chart()

    def _on_theme_change(self) -> None:
        self._update_canvas_colors()
        self._plot_asset_history()
        self._plot_trade_volume_chart()

    def _update_canvas_colors(self) -> None:
        style = ttk.Style()
        bg_color = self.winfo_rgb(style.lookup("TFrame", "background") or "#FFFFFF")
        bg_color = '#%02x%02x%02x' % tuple(c // 256 for c in bg_color)
        self._figure.set_facecolor(bg_color)
        self._ax1.set_facecolor(bg_color)
        self._ax2.set_facecolor(bg_color)
        fg_color = self.winfo_rgb(style.lookup("TFrame", "foreground") or "#000000")
        self._fg_color = '#%02x%02x%02x' % tuple(c // 256 for c in fg_color)

    def _plot_chart(self, ax: Axes, data: pd.Series, **plot_kwargs: Any) -> None:
        ax.clear()
        data.plot(ax=ax, **plot_kwargs)
        # Theme-based coloring
        ax.tick_params(colors=self._fg_color)
        ax.xaxis.label.set_color(self._fg_color)
        ax.yaxis.label.set_color(self._fg_color)
        ax.title.set_color(self._fg_color)
        for spine in ax.spines.values():
            spine.set_color(self._fg_color)
        if plot_kwargs.get("kind") == "pie":
            for text in ax.texts:
                if '%' in text.get_text():
                    text.set_color('black')
        # Drawing plot changes
        self._canvas.draw()
        self._figure.tight_layout()

    def _plot_asset_history(self) -> None:
        currency = self._controller.selected_currency.get()
        asset_history = self._controller.service.get_crypto_history(asset_id=self._asset_id)
        self._plot_chart(self._ax1, asset_history, xlabel="Date", ylabel=currency,
                         title=f"Price History for \"{self._asset_id}\"", grid=True)

        cursor = mplcursors.cursor(self._ax1, hover=mplcursors.HoverMode.Transient)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            f"{Formatter.format_price(sel.target[1])} {currency}  on {Formatter.format_date(sel.target[0])}"
        ))

    def _plot_trade_volume_chart(self) -> None:
        selected_items = self._tree.selection()
        if not selected_items:
            selected_items = self._tree.get_children()

        columns = self._tree["columns"]
        data = [self._tree.item(item, "values") for item in selected_items]
        df = pd.DataFrame(data, columns=columns)

        target_values = df["Volume (24H)"].astype(float).values
        target_index = (df["Exchange (ID)"] + " | " + df["Base (Symbol)"] + "/" + df["Quote (Symbol)"]).values
        if len(selected_items) == len(df):
            threshold = 0.03 * target_values.sum()
            target_index = [name if value >= threshold else "Others" for name, value in zip(target_index, target_values)]

        market_shares = pd.Series(target_values, index=target_index).groupby(level=0).sum()

        def format_pct(pct: float) -> str:
            absolute = int(pct / 100. * market_shares.sum())
            return f"{pct:.1f}%\n{Formatter.human_format(absolute)} {self._controller.selected_currency.get()}"

        self._plot_chart(self._ax2, market_shares, kind="pie", autopct=format_pct, textprops={'color': self._fg_color},
                         title=f"\"{self._asset_id}\" Trading Volume Share by Exchange and Pair")
