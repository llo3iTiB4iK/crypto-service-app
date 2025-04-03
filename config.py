import os

# Application config
APP_TITLE = ""
ICON_PATH = "icon.ico"

# Data source config
API_BASE_URL = "https://rest.coincap.io/v3"
API_BEARER_TOKEN = os.environ.get("COINCAP_API_KEY")

# Single pages config
PAGE_REFRESH_TIME_SEC = 60
MAIN_PAGE_SEARCH_DELAY_MS = 200
MARKETS_PAGE_PLOT_DELAY_MS = 500
