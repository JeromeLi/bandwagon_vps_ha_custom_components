"""Constants for the BandwagonHost (KiwiVM) integration."""
from datetime import timedelta

DOMAIN = "bandwagonhost"
CONF_VEID = "veid"
CONF_API_KEY = "api_key"

API_BASE_URL = "https://api.64clouds.com/v1"

# The update interval to avoid getting banned
UPDATE_INTERVAL = timedelta(minutes=5)
