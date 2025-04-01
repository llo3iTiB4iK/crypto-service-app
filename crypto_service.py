import requests
import pandas as pd


class CryptoService:
    BASE_URL = "https://api.coincap.io/v2"

    @staticmethod
    def _get_data(url: str, params: dict = None) -> pd.DataFrame:
        try:
            response = requests.get(url, params, timeout=10)
            response.raise_for_status()
            json_data = response.json()
            if "data" not in json_data:
                print(f"Unexpected response format: {json_data}")
                return pd.DataFrame()
            return pd.DataFrame(json_data["data"])
        except requests.RequestException as e:
            print(f"Request Exception: {e}")
            return pd.DataFrame()

    def get_asset_price(self, n_rows: int = None) -> pd.DataFrame:
        url = f"{self.BASE_URL}/assets"
        data = self._get_data(url, {"limit": n_rows})
        if data.empty:
            return data

        data.set_index("id", inplace=True)
        data = data[["symbol", "name", "priceUsd", "changePercent24Hr"]]
        return data

    def get_crypto_markets(self, asset_id: str) -> pd.DataFrame:
        url = f"{self.BASE_URL}/assets/{asset_id}/markets"
        data = self._get_data(url)
        if data.empty:
            return data

        data.set_index(["baseId", "quoteId"], append=True, inplace=True)
        data = data[["exchangeId", "baseSymbol", "quoteSymbol", "priceUsd", "volumeUsd24Hr", "volumePercent"]]
        data.rename({
            "exchangeId": "Exchange (ID)",
            "baseSymbol": "Base (Symbol)",
            "quoteSymbol": "Quote (Symbol)",
            "priceUsd": "Price (USD)",
            "volumeUsd24Hr": "Volume (24H)",
            "volumePercent": "Volume (%)"
        }, axis=1, inplace=True)
        return data

    def get_crypto_history(self, asset_id: str) -> pd.Series:
        url = f"{self.BASE_URL}/assets/{asset_id}/history"
        data = self._get_data(url, {'interval': 'd1'})
        if data.empty:
            return pd.Series(dtype=float)

        return pd.Series(data["priceUsd"].astype(float).values, index=pd.to_datetime(data["time"], unit="ms"))
