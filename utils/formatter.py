import matplotlib.dates as mdates


class Formatter:

    @staticmethod
    def human_format(num: float) -> str:
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        return str(num)

    @staticmethod
    def format_price(price: float) -> str:
        return f"{price:.2e}" if price < 0.01 else f"{price:.2f}"

    @staticmethod
    def format_date(matplotlib_date: float) -> str:
        return mdates.num2date(matplotlib_date).strftime('%Y-%m-%d')
