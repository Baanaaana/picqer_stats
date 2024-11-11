import logging
from homeassistant.helpers.entity import Entity
import requests
from requests.auth import HTTPBasicAuth
from .const import DOMAIN
from datetime import timedelta

# Set up logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    api_key = config_entry.data["api_key"]
    store_url_prefix = config_entry.data["store_url_prefix"]

    # Static sensors for Picqer stats
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
        PicqerInactiveProductsSensor(api_key, store_url_prefix)
    ]
    async_add_entities(sensors, True)

    # Dynamic batch sensors for uncompleted picklists
    batch_sensor_manager = PicqerBatchSensorManager(api_key, store_url_prefix, hass, async_add_entities)
    await batch_sensor_manager.update_sensors()

    # Periodic update for uncompleted picklist batches
    hass.helpers.event.async_track_time_interval(
        lambda now: batch_sensor_manager.update_sensors(),
        timedelta(minutes=5)  # Adjust interval as needed
    )

class PicqerBatchSensorManager:
    def __init__(self, api_key, store_url_prefix, hass, async_add_entities):
        self._api_key = api_key
        self._store_url_prefix = store_url_prefix
        self._hass = hass
        self._async_add_entities = async_add_entities
        self._sensors = {}

    async def update_sensors(self):
        """Fetch uncompleted batches and update sensors accordingly."""
        url = f"https://{self._store_url_prefix}.picqer.com/api/v1/picklists/batches"
        try:
            _LOGGER.info("Fetching uncompleted batches from Picqer API...")
            response = requests.get(url, auth=HTTPBasicAuth(self._api_key, ""))
            response.raise_for_status()
            data = response.json()

            _LOGGER.debug(f"API Response Data: {data}")

            # Filter uncompleted batches
            uncompleted_batches = [
                batch for batch in data if batch.get("status") != "completed"
            ]
            _LOGGER.info(f"Found {len(uncompleted_batches)} uncompleted batches.")

            new_sensors = []
            for batch in uncompleted_batches:
                batch_id = batch["idbatch"]
                if batch_id not in self._sensors:
                    _LOGGER.info(f"Creating sensor for batch ID: {batch_id}")
                    sensor = PicqerBatchSensor(batch)
                    self._sensors[batch_id] = sensor
                    new_sensors.append(sensor)
                else:
                    self._sensors[batch_id].update_data(batch)
                    _LOGGER.info(f"Updating sensor for batch ID: {batch_id}")

            # Add any new sensors to Home Assistant
            if new_sensors:
                self._async_add_entities(new_sensors, True)

        except requests.exceptions.HTTPError as err:
            _LOGGER.error(f"Error fetching batches from Picqer: {err}")

class PicqerBatchSensor(Entity):
    def __init__(self, batch_data):
        self._batch_data = batch_data
        self._state = batch_data.get("status")

    @property
    def name(self):
        return f"Picqer Batch {self._batch_data['idbatch']}"

    @property
    def unique_id(self):
        return f"picqer_batch_{self._batch_data['idbatch']}"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {
            "batch_id": self._batch_data["idbatch"],
            "person_name": self._batch_data.get("person_name"),
            "type": self._batch_data.get("type"),
            "status": self._batch_data.get("status")
        }

    def update_data(self, new_data):
        self._batch_data = new_data
        self._state = new_data.get("status")
        self.schedule_update_ha_state()

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
        url = f"https://{self._store_url_prefix}.picqer.com/api/v1/{self._endpoint}"
        try:
            response = requests.get(url, auth=HTTPBasicAuth(self._api_key, ""))
            response.raise_for_status()
            data = response.json()
            if "value" in data:
                self._state = data["value"]
            else:
                self._state = "Error: No value field"
        except requests.exceptions.HTTPError as err:
            self._state = "Error"
            _LOGGER.error(f"HTTP error for {self._name}: {err}")
        except requests.exceptions.RequestException as req_err:
            self._state = "Error: Cannot reach API"
            _LOGGER.error(f"Request error for {self._name}: {req_err}")
        except Exception as e:
            self._state = "Error"
            _LOGGER.error(f"Unexpected error for {self._name}: {e}")

# Static sensors with specific unit of measurement
class PicqerOpenPicklistsSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Open Picklists", "stats/open-picklists", "picqer_open_picklists")
    @property
    def unit_of_measurement(self):
        return "Picklists"

class PicqerOpenOrdersSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Open Orders", "stats/open-orders", "picqer_open_orders")
    @property
    def unit_of_measurement(self):
        return "orders"

class PicqerNewOrdersTodaySensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer New Orders Today", "stats/new-orders-today", "picqer_new_orders_today")
    @property
    def unit_of_measurement(self):
        return "orders"

class PicqerNewOrdersThisWeekSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer New Orders This Week", "stats/new-orders-this-week", "picqer_new_orders_this_week")
    @property
    def unit_of_measurement(self):
        return "orders"

class PicqerClosedPicklistsThisWeekSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Closed Picklists This Week", "stats/closed-picklists-this-week", "picqer_closed_picklists_this_week")
    @property
    def unit_of_measurement(self):
        return "Picklists"

class PicqerTotalOrdersSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Total Orders", "stats/total-orders", "picqer_total_orders")
    @property
    def unit_of_measurement(self):
        return "orders"

class PicqerBackordersSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Backorders", "stats/backorders", "picqer_backorders")
    @property
    def unit_of_measurement(self):
        return "orders"

class PicqerClosedPicklistsTodaySensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Closed Picklists Today", "stats/closed-picklists-today", "picqer_closed_picklists_today")
    @property
    def unit_of_measurement(self):
        return "Picklists"

class PicqerNewCustomersThisWeekSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer New Customers This Week", "stats/new-customers-this-week", "picqer_new_customers_this_week")
    @property
    def unit_of_measurement(self):
        return "customers"

class PicqerTotalProductsSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Total Products", "stats/total-products", "picqer_total_products")
    @property
    def unit_of_measurement(self):
        return "products"

class PicqerActiveProductsSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Active Products", "stats/active-products", "picqer_active_products")
    @property
    def unit_of_measurement(self):
        return "products"

class PicqerInactiveProductsSensor(PicqerBaseSensor):
    def __init__(self, api_key, store_url_prefix):
        super().__init__(api_key, store_url_prefix, "Picqer Inactive Products", "stats/inactive-products", "picqer_inactive_products")
    @property
    def unit_of_measurement(self):
        return "products"
