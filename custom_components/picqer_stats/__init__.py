import asyncio
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import requests
from requests.auth import HTTPBasicAuth
import logging
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault("picqer_stats", {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data["picqer_stats"][entry.entry_id] = entry.data

    # Register the reset batch service
    async def handle_reset_batch_service(call):
        batch_id = call.data.get("batch_id")
        api_key = entry.data["api_key"]
        store_url_prefix = entry.data["store_url_prefix"]
        
        # Call the Picqer API to reset the batch
        url = f"https://{store_url_prefix}.picqer.com/api/v1/picklists/batches/{batch_id}/reset"
        response = requests.post(url, auth=HTTPBasicAuth(api_key, ""))
        
        if response.status_code == 200:
            _LOGGER.info(f"Batch {batch_id} reset successfully.")
        else:
            _LOGGER.error(f"Failed to reset batch {batch_id}: {response.text}")

    hass.services.async_register(
        DOMAIN, "reset_batch", handle_reset_batch_service, schema=vol.Schema({
            vol.Required("batch_id"): str,
        })
    )

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data["picqer_stats"].pop(entry.entry_id)
    return unload_ok
