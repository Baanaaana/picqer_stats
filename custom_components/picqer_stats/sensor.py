import logging
from datetime import datetime, timedelta
from homeassistant.helpers.entity import Entity
import requests
from requests.auth import HTTPBasicAuth
from .const import DOMAIN, ATTR_PICKER_NAME, ATTR_BATCH_TYPE, ATTR_TOTAL_PRODUCTS, ATTR_TOTAL_PICKLISTS, ATTR_CREATED_AT, ATTR_DURATION, DEFAULT_SCAN_INTERVAL
from collections import defaultdict
from typing import Any, Dict

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Picqer sensors."""
    api_key = config_entry.data["api_key"]
    store_url_prefix = config_entry.data["store_url_prefix"]

    sensors = [
        PicqerBatchSensor(api_key, store_url_prefix),
        # Add other sensors here
    ]
    
    async_add_entities(sensors, True)

class PicqerBatchSensor(Entity):
    """Representation of a Picqer Batch sensor."""
    
    def __init__(self, api_key, store_url_prefix):
        self._api_key = api_key
        self._store_url_prefix = store_url_prefix
        self._name = "Picqer Batches"
        self._state = None
        self._attrs: Dict[str, Any] = {}

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attrs

    def update(self):
        """Fetch new state data for the sensor."""
        url = f"https://{self._store_url_prefix}.picqer.com/api/v1/picklists/batches"
        try:
            response = requests.get(url, auth=HTTPBasicAuth(self._api_key, ""))
            response.raise_for_status()
            data = response.json()

            today_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_batches = []

            for batch in data:
                created_at = datetime.strptime(batch["created_at"], "%Y-%m-%d %H:%M:%S")
                if created_at >= today_midnight:
                    today_batches.append({
                        "id": batch["id"],
                        ATTR_PICKER_NAME: batch["assigned_to"]["full_name"] if batch["assigned_to"] else "Unassigned",
                        ATTR_BATCH_TYPE: batch["type"],
                        ATTR_TOTAL_PRODUCTS: batch["total_products"],
                        ATTR_TOTAL_PICKLISTS: batch["total_picklists"],
                        ATTR_CREATED_AT: batch["created_at"],
                        ATTR_DURATION: str(datetime.now() - created_at).split(".")[0],
                        "status": batch["status"]
                    })

            self._state = len(today_batches)
            self._attrs.update({"batches": today_batches})

        except requests.exceptions.RequestException as err:
            self._state = "Error"
            _LOGGER.error(f"Error fetching batch data: {err}")
