import logging
from homeassistant.helpers.entity import Entity
import requests
from requests.auth import HTTPBasicAuth
from .const import DOMAIN

# Set up logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    api_key = config_entry.data["api_key"]
    store_url_prefix = config_entry.data["store_url_prefix"]

    # Create sensor instances for each valid endpoint, using the store URL prefix
    sensors = [
        PicqerOpenPicklistsSensor(api_key, store_url_prefix),
        PicqerOpenOrdersSensor(api_key, store_url_prefix),
        PicqerNewOrdersTodaySensor(api_key, store_url_prefix),
        PicqerNewOrdersThisWeekSensor(api_key, store_url_prefix),
        PicqerClosedPicklistsThisWeekSensor(api_key, store_url_prefix),
        PicqerTotalOrdersSensor(api_key, store_url_prefix),
        PicqerBackordersSensor(api_key, store_url_prefix),
    ]
    async_add_entities(sensors, True)

class PicqerBaseSensor(Entity):
    def __init__(self, api_key, store_url_prefix, name, endpoint, unique_id):
        self._api_key = api_key
        self._store_url_prefix = store_url_prefix
        self._name = name
        self._endpoint = endpoint
        self._unique_id = unique_id
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return "mdi:asterisk-circle-outline"

    def update(self):
        # Build the URL dynamically using the store URL prefix
        url = f"https://{self._store_url_prefix}.picqer.com/api/v1/{self._endpoint}"
        try:
            _LOGGER.info(f"Requesting data from {url} for {self._name}")
            response = requests.get(url, auth=HTTPBasicAuth(self._api_key, ""))
            _LOGGER.info(f"Received status code {response.status_code} from {url}")
            response.raise_for_status()
            data = response.json()

            # Log the response data for debugging purposes
            _LOGGER.debug(f"API Response for {self._name}: {data}")

            # Set the state based on "value" if present; otherwise, log an error
            if "value" in data:
                self._state = data["value"]
            else:
                self._state = "Error: No value field"
                _LOGGER.error(f"No 'value' field found in response for {self._name}")

        except requests.exceptions.HTTPError as err:
            self._state = "Error"
            _LOGGER.error(f"HTTP error for {self._name}: {err}")
        except requests.exceptions.RequestException as req_err:
            self._state = "Error: Cannot reach API"
            _LOGGER.error(f"Request error for {self._name}: {req_err}")
        except Exception as e:
            self._state = "Error"
            _LOGGER.error(f"Unexpected error for {self._name}: {e}")

# Define each sensor with its specific endpoint and unique ID
class PicqerOpenPicklistsSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Open Picklists", "stats/open-picklists", "picqer_open_picklists")

class PicqerOpenOrdersSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Open Orders", "stats/open-orders", "picqer_open_orders")

class PicqerNewOrdersTodaySensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer New Orders Today", "stats/new-orders-today", "picqer_new_orders_today")

class PicqerNewOrdersThisWeekSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer New Orders This Week", "stats/new-orders-this-week", "picqer_new_orders_this_week")

class PicqerClosedPicklistsThisWeekSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Closed Picklists This Week", "stats/closed-picklists-this-week", "picqer_closed_picklists_this_week")

class PicqerTotalOrdersSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Total Orders", "stats/total-orders", "picqer_total_orders")

class PicqerBackordersSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Backorders", "stats/backorders", "picqer_backorders")
