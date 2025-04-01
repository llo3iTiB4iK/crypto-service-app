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
        self.asset_id = None
        # Back button
        self.back_button = tk.Button(self, text="< Back", command=lambda: self.controller.show_frame("MainPage"))
        # Matplotlib Figure for price history
        self.figure = Figure(figsize=(12, 5), dpi=50)  # todo: adjust size
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        # Toolbar для масштабування/переміщення графіка
        self.toolbar = NavigationToolbar2Tk(self.canvas, window=self, pack_toolbar=False)
        # Setup frame
        self.place_widgets()

    def place_widgets(self) -> None:
        self.back_button.grid(row=0, column=0)
        self.tree.grid(row=1, column=0)
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        self.toolbar.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.canvas.get_tk_widget().grid(row=3, column=0, columnspan=2, sticky="nsew")

    def update_page(self) -> None:
        asset_markets = self.controller.service.get_crypto_markets(asset_id=self.asset_id)
        self.fill_treeview(asset_markets)
        asset_history = self.controller.service.get_crypto_history(asset_id=self.asset_id)
        self._plot_price_chart(asset_history)

    def set_asset(self, asset_id: str):
        self.stop_refreshing()
        self.asset_id = asset_id
        self.refresh()

    def _plot_price_chart(self, *plot_args: Any) -> None:
        ax = self.plot_data(*plot_args, self.figure,
                            xlabel="Date", ylabel="Price (USD)", title=f"Price History for {self.asset_id}", grid=True)

        def format_price(price: float) -> str:
            return f"{price:.2e}" if price < 0.01 else f"{price:.2f}"

        cursor = mplcursors.cursor(ax, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            f"${format_price(sel.target[1])} on {mdates.num2date(sel.target[0]).strftime('%Y-%m-%d')}"
        ))

        self.canvas.draw()
        self.figure.tight_layout()
        self.toolbar.update()
