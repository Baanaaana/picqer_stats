import asyncio
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault("picqer_stats", {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data["picqer_stats"][entry.entry_id] = entry.data
    # Changed from async_forward_entry_setup to await async_forward_entry_setups
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data["picqer_stats"].pop(entry.entry_id)
    return unload_ok
