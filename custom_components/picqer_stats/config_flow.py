import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class PicqerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Save both the API key and the Store URL Prefix
            return self.async_create_entry(
                title="Picqer Stats",
                data={
                    "api_key": user_input["api_key"],
                    "store_url_prefix": user_input["store_url_prefix"]
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("store_url_prefix"): str,
                vol.Required("api_key"): str,
            }),
        )
