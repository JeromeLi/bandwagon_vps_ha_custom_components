"""Config flow for BandwagonHost (KiwiVM) integration."""
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_BASE_URL, CONF_API_KEY, CONF_VEID, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_VEID): str,
        vol.Required(CONF_API_KEY): str,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    veid = data[CONF_VEID]
    api_key = data[CONF_API_KEY]
    
    session = async_get_clientsession(hass)
    # Using migrate/getLocations as a lightweight endpoint just to check auth
    url = f"{API_BASE_URL}/migrate/getLocations"
    params = {"veid": veid, "api_key": api_key}
    
    try:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status != 200:
                _LOGGER.error("API HTTP Status: %s", response.status)
                raise CannotConnect
            # Force aiohttp to parse JSON regardless of the 'text/plain' Content-Type header
            result = await response.json(content_type=None)
            error_code = result.get("error", 0)
            
            # API returns error 733104 for invalid VEID/API KEY
            # If we get 0 (Success) or 733102 (Auth success, but plan doesn't support migrations)
            # then we know the credentials are correct.
            if error_code not in (0, 733102):
                _LOGGER.error("API returned authentication error: %s", result)
                raise CannotConnect
    except Exception as err:
        _LOGGER.error("Failed to authenticate KiwiVM API: %s", err)
        raise CannotConnect from err

    # Return info that you want to store in the config entry.
    return {"title": data[CONF_NAME], "veid": veid}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BandwagonHost."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            # Check if this VEID is already added
            await self.async_set_unique_id(user_input[CONF_VEID])
            self._abort_if_unique_id_configured()

            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
