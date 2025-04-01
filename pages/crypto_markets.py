import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.dates as mdates
import mplcursors
from typing import TYPE_CHECKING, Any
from .base_page import BasePage

if TYPE_CHECKING:
    from app import MyApp


class CryptoMarkets(BasePage):
    def __init__(self, parent: tk.Frame, controller: "MyApp") -> None:
        super().__init__(parent, controller, {"columns": [], "show": "headings"})
        self._tree.bind("<<TreeviewSelect>>", self._on_tree_selection_change)
        self._asset_id = None
        # Back button
        self._back_button = tk.Button(self, text="< Back", command=lambda: self._controller.show_frame("MainPage"))
        # Matplotlib Figure for price history
        self._figure = Figure(figsize=(12, 5), dpi=50)  # todo: adjust size
        self._canvas = FigureCanvasTkAgg(self._figure, master=self)
        # Toolbar для масштабування/переміщення графіка
        self._toolbar = NavigationToolbar2Tk(self._canvas, window=self, pack_toolbar=False)
        # Setup frame
        self._place_widgets()

    def _place_widgets(self) -> None:
        self._back_button.grid(row=0, column=0)
        self._tree.grid(row=1, column=0)
        self._scrollbar.grid(row=1, column=1, sticky="ns")
        self._toolbar.grid(row=2, column=0, columnspan=2, sticky="ew")
        self._canvas.get_tk_widget().grid(row=3, column=0, columnspan=2, sticky="nsew")

    def _update_page(self) -> None:
        asset_markets = self._controller.service.get_crypto_markets(asset_id=self._asset_id)
        self._fill_treeview(asset_markets)
        asset_history = self._controller.service.get_crypto_history(asset_id=self._asset_id)
        self._plot_price_chart(asset_history)

    def _on_tree_selection_change(self, event: tk.Event) -> None:
        print(event)
        selected_items = self._tree.selection()
        if selected_items:
            print(f"Вибрано: {selected_items}")

    def set_asset(self, asset_id: str) -> None:
        self._stop_refreshing()
        self._asset_id = asset_id
        self._refresh()

    def _plot_price_chart(self, *plot_args: Any) -> None:
        ax = self._plot_data(*plot_args, self._figure,
                             xlabel="Date", ylabel="Price (USD)", title=f"Price History for {self._asset_id}", grid=True)

        def format_price(price: float) -> str:
            return f"{price:.2e}" if price < 0.01 else f"{price:.2f}"

        cursor = mplcursors.cursor(ax, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            f"${format_price(sel.target[1])} on {mdates.num2date(sel.target[0]).strftime('%Y-%m-%d')}"
        ))

        self._canvas.draw()
        self._figure.tight_layout()
        self._toolbar.update()
