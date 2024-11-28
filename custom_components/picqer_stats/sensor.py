import logging
from datetime import datetime, timedelta
from homeassistant.helpers.entity import Entity
import requests
from requests.auth import HTTPBasicAuth
from .const import DOMAIN

# Set up logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    api_key = config_entry.data["api_key"]
    store_url_prefix = config_entry.data["store_url_prefix"]

    sensors = [
        PicqerOpenPicklistsSensor(api_key, store_url_prefix),
        PicqerOpenOrdersSensor(api_key, store_url_prefix),
        PicqerNewOrdersTodaySensor(api_key, store_url_prefix),
        PicqerNewOrdersThisWeekSensor(api_key, store_url_prefix),
        PicqerClosedPicklistsThisWeekSensor(api_key, store_url_prefix),
        PicqerTotalOrdersSensor(api_key, store_url_prefix),
        PicqerBackordersSensor(api_key, store_url_prefix),
        PicqerClosedPicklistsTodaySensor(api_key, store_url_prefix),
        PicqerNewCustomersThisWeekSensor(api_key, store_url_prefix),
        PicqerTotalProductsSensor(api_key, store_url_prefix),
        PicqerActiveProductsSensor(api_key, store_url_prefix),
        PicqerInactiveProductsSensor(api_key, store_url_prefix),
        PicqerClosedPicklists7DaysAgoSensor(api_key, store_url_prefix)
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

    @property
    def should_poll(self):
        return True

    def update(self):
        url = f"https://{self._store_url_prefix}.picqer.com/api/v1/{self._endpoint}"
        try:
            _LOGGER.info(f"Requesting data from {url} for {self._name}")
            response = requests.get(url, auth=HTTPBasicAuth(self._api_key, ""))
            _LOGGER.info(f"Received status code {response.status_code} from {url}")
            response.raise_for_status()
            data = response.json()
            _LOGGER.debug(f"API Response for {self._name}: {data}")

            if "value" in data:
                self._state = data["value"]
            else:
                self._state = "Error: No value field"
                _LOGGER.error(f"No 'value' field found in response for {self._name}")

        except requests.exceptions.RequestException as err:
            self._state = "Error"
            _LOGGER.error(f"Error for {self._name}: {err}")

class PicqerOpenPicklistsSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Open Picklists", "stats/open-picklists", "picqer_open_picklists")

    @property
    def unit_of_measurement(self):
        return "orders"

    @property
    def state_class(self):
        return "measurement"

class PicqerOpenOrdersSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Open Orders", "stats/open-orders", "picqer_open_orders")

    @property
    def unit_of_measurement(self):
        return "orders"

    @property
    def state_class(self):
        return "measurement"

class PicqerNewOrdersTodaySensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer New Orders Today", "stats/new-orders-today", "picqer_new_orders_today")

    @property
    def unit_of_measurement(self):
        return "orders"

    @property
    def state_class(self):
        return "measurement"

class PicqerNewOrdersThisWeekSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer New Orders This Week", "stats/new-orders-this-week", "picqer_new_orders_this_week")

    @property
    def unit_of_measurement(self):
        return "orders"

    @property
    def state_class(self):
        return "measurement"

class PicqerClosedPicklistsThisWeekSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Closed Picklists This Week", "stats/closed-picklists-this-week", "picqer_closed_picklists_this_week")

    @property
    def unit_of_measurement(self):
        return "orders"

    @property
    def state_class(self):
        return "measurement"

class PicqerTotalOrdersSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Total Orders", "stats/total-orders", "picqer_total_orders")

    @property
    def unit_of_measurement(self):
        return "orders"

    @property
    def state_class(self):
        return "total_increasing"

class PicqerBackordersSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Backorders", "stats/backorders", "picqer_backorders")

    @property
    def unit_of_measurement(self):
        return "orders"

    @property
    def state_class(self):
        return "measurement"

class PicqerClosedPicklistsTodaySensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Closed Picklists Today", "stats/closed-picklists-today", "picqer_closed_picklists_today")

    @property
    def unit_of_measurement(self):
        return "orders"

    @property
    def state_class(self):
        return "measurement"

class PicqerNewCustomersThisWeekSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer New Customers This Week", "stats/new-customers-this-week", "picqer_new_customers_this_week")

    @property
    def unit_of_measurement(self):
        return "customers"

    @property
    def state_class(self):
        return "measurement"

class PicqerTotalProductsSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Total Products", "stats/total-products", "picqer_total_products")

    @property
    def unit_of_measurement(self):
        return "products"

    @property
    def state_class(self):
        return "measurement"

class PicqerActiveProductsSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Active Products", "stats/active-products", "picqer_active_products")

    @property
    def unit_of_measurement(self):
        return "products"

    @property
    def state_class(self):
        return "measurement"

class PicqerInactiveProductsSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Inactive Products", "stats/inactive-products", "picqer_inactive_products")

    @property
    def unit_of_measurement(self):
        return "products"

    @property
    def state_class(self):
        return "measurement"

class PicqerClosedPicklists7DaysAgoSensor(PicqerBaseSensor):
    """Sensor for closed picklists from exactly 7 days ago."""
    
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Closed Picklists 7 Days Ago", "picklists", "picqer_closed_picklists_7_days_ago")

    def update(self):
        # Calculate the date range for exactly 7 days ago
        target_date = datetime.now().date() - timedelta(days=7)
        start_date = target_date.strftime('%Y-%m-%d 00:00:00')
        end_date = target_date.strftime('%Y-%m-%d 23:59:59')
        
        # Build base URL with query parameters
        params = {
            'status': 'closed',
            'closed_after': start_date,
            'closed_before': end_date,
            'offset': 0,
            'limit': 100  # Maximum items per page
        }
        
        url = f"https://{self._store_url_prefix}.picqer.com/api/v1/{self._endpoint}"
        total_picklists = 0
        
        try:
            while True:
                _LOGGER.debug(f"Requesting page with offset {params['offset']}")
                response = requests.get(url, params=params, auth=HTTPBasicAuth(self._api_key, ""))
                _LOGGER.info(f"Received status code {response.status_code} from {url}")
                response.raise_for_status()
                data = response.json()
                
                if not isinstance(data, list):
                    self._state = "Error: Invalid response format"
                    _LOGGER.error(f"Invalid response format for {self._name}: {data}")
                    return

                batch_size = len(data)
                _LOGGER.debug(f"Received {batch_size} picklists in this batch")
                total_picklists += batch_size
                _LOGGER.debug(f"Running total: {total_picklists}")
                
                # If we got no results or less than the limit, we've reached the end
                if batch_size == 0 or batch_size < params['limit']:
                    _LOGGER.debug(f"Reached end of results with total: {total_picklists}")
                    break
                
                # Prepare for next page
                params['offset'] += params['limit']
                _LOGGER.debug(f"Moving to next page with offset: {params['offset']}")

            _LOGGER.info(f"Final total picklists count: {total_picklists}")
            self._state = total_picklists

        except requests.exceptions.RequestException as err:
            self._state = "Error"
            _LOGGER.error(f"Error for {self._name}: {err}")

    @property
    def unit_of_measurement(self):
        return "orders"

    @property
    def state_class(self):
        return "measurement"
