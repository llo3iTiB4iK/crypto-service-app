import requests
import pandas as pd
import os


class CryptoService:
    BASE_URL = "https://rest.coincap.io/v3"
    API_KEY = os.environ.get("COINCAP_API_KEY")

    def __init__(self) -> None:
        self.session = requests.Session()

    def _request_data(self, endpoint: str, params: dict = None) -> pd.DataFrame:
        if params is None:
            params = {}

        params["apiKey"] = self.API_KEY
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return pd.DataFrame(data.get("data"))
        except requests.RequestException as e:
            print(f"Request Exception: {e}")
            return pd.DataFrame()

    def get_asset_price(self, n_rows: int = None) -> pd.DataFrame:
        df = self._request_data("assets", {"limit": n_rows})
        if df.empty:
            return df

        return df.set_index("id")[["symbol", "name", "priceUsd", "changePercent24Hr"]]

    def get_crypto_markets(self, asset_id: str) -> pd.DataFrame:
        df = self._request_data(f"assets/{asset_id}/markets")
        if df.empty:
            return df

        return df[["exchangeId", "baseSymbol", "quoteSymbol", "priceUsd", "volumeUsd24Hr", "volumePercent"]].rename(
            columns={
                "exchangeId": "Exchange (ID)",
                "baseSymbol": "Base (Symbol)",
                "quoteSymbol": "Quote (Symbol)",
                "priceUsd": "Price (USD)",
                "volumeUsd24Hr": "Volume (24H)",
                "volumePercent": "Volume (%)"
            })

    def get_crypto_history(self, asset_id: str) -> pd.Series:
        df = self._request_data(f"assets/{asset_id}/history", {"interval": "d1"})
        if df.empty:
            return pd.Series(dtype=float)

        return pd.Series(df["priceUsd"].astype(float).values, index=pd.to_datetime(df["time"], unit="ms"))
