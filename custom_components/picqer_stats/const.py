"""Constants for the Picqer Stats integration."""
from datetime import timedelta

DOMAIN = "picqer_stats"
CONF_API_KEY = "api_key"
CONF_URL_PREFIX = "store_url_prefix"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)

# Batch attributes
ATTR_PICKER_NAME = "picker_name"
ATTR_BATCH_TYPE = "batch_type"
ATTR_TOTAL_PRODUCTS = "total_products"
ATTR_TOTAL_PICKLISTS = "total_picklists"
ATTR_CREATED_AT = "created_at"
ATTR_DURATION = "duration"