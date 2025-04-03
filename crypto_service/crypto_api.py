import requests
import pandas as pd
from config import API_BASE_URL, API_BEARER_TOKEN


class CryptoAPI:
    BASE_URL = API_BASE_URL
    API_KEY = API_BEARER_TOKEN

    def __init__(self) -> None:
        self._session = requests.Session()

    def request_data(self, endpoint: str, params: dict = None) -> pd.DataFrame:
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
