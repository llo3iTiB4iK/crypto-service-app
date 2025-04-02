import requests
import pandas as pd
import os


class CryptoService:
    BASE_URL = "https://rest.coincap.io/v3"
    API_KEY = os.environ.get("COINCAP_API_KEY")

    def __init__(self) -> None:
        self._session = requests.Session()
        self.conversion_rate = 1

    def _request_data(self, endpoint: str, params: dict = None) -> pd.DataFrame:
        if params is None:
            params = {}

        params["apiKey"] = self.API_KEY
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = self._session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return pd.DataFrame(data.get("data"))
        except requests.RequestException as e:
            print(f"Request Exception: {e}")
            return pd.DataFrame()

    def _apply_conversion_rate(self, data: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
        return data.astype(float) / self.conversion_rate

    def get_asset_price(self, n_rows: int = None) -> pd.DataFrame:
        df = self._request_data("assets", {"limit": n_rows})
        if df.empty:
            return df

        df["priceUsd"] = self._apply_conversion_rate(df["priceUsd"])
        return df.set_index("id")[["symbol", "name", "priceUsd", "changePercent24Hr"]]

    def get_crypto_markets(self, asset_id: str) -> pd.DataFrame:
        df = self._request_data(f"assets/{asset_id}/markets")
        if df.empty:
            return df

        df[["priceUsd", "volumeUsd24Hr"]] = self._apply_conversion_rate(df[["priceUsd", "volumeUsd24Hr"]])
        return df[["exchangeId", "baseSymbol", "quoteSymbol", "priceUsd", "volumeUsd24Hr", "volumePercent"]].rename(
            columns={
                "exchangeId": "Exchange (ID)",
                "baseSymbol": "Base (Symbol)",
                "quoteSymbol": "Quote (Symbol)",
                "priceUsd": "Price",
                "volumeUsd24Hr": "Volume (24H)",
                "volumePercent": "Volume (%)"
            })

    def get_crypto_history(self, asset_id: str) -> pd.Series:
        df = self._request_data(f"assets/{asset_id}/history", {"interval": "d1"})
        if df.empty:
            return pd.Series(dtype=float)

        df["priceUsd"] = self._apply_conversion_rate(df["priceUsd"])
        return pd.Series(df["priceUsd"].values, index=pd.to_datetime(df["time"], unit="ms"))

    def get_conversion_rates(self) -> pd.Series:
        df = self._request_data("rates")
        if df.empty:
            return pd.Series(dtype=float)

        result_index = df["symbol"] + df["currencySymbol"].fillna("").apply(lambda x: f" ({x})" if x else "")
        return pd.Series(df["rateUsd"].astype(float).values, index=result_index)
