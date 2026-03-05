import asyncio
import logging

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_BASE_URL, DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class KiwiVMDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching KiwiVM API data."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        veid: str,
        api_key: str,
    ) -> None:
        """Initialize."""
        self.veid = veid
        self.api_key = api_key
        self.vps_name = name

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            # We use an aiohttp client session for non-blocking HTTP requests
            async with aiohttp.ClientSession() as session:
                params = {
                    "veid": self.veid,
                    "api_key": self.api_key
                }
                
                # Fetch live status
                url = f"{API_BASE_URL}/getLiveServiceInfo"
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=45)) as response:
                    response.raise_for_status()
                    # KiwiVM API returns text/plain, bypassing strict content-type check
                    data = await response.json(content_type=None)
                    
                    if data.get("error") != 0:
                        raise UpdateFailed(f"Error fetching KiwiVM data: {data.get('message', 'Unknown API Error')}")

                    return data
        except asyncio.TimeoutError as err:
            raise UpdateFailed(f"Timeout communicating with API: {err}")
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
        except Exception as err:
            raise UpdateFailed(f"Unexpected error communicating with API: {err}")

    async def async_send_command(self, command: str) -> bool:
        """Send a power control command (start, stop, restart) to the VPS."""
        if command not in ["start", "stop", "restart"]:
            _LOGGER.error("Invalid command: %s", command)
            return False

        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "veid": self.veid,
                    "api_key": self.api_key
                }
                url = f"{API_BASE_URL}/{command}"
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=45)) as response:
                    response.raise_for_status()
                    # Bypass strict content-type check
                    data = await response.json(content_type=None)
                    
                    if data.get("error") != 0:
                        _LOGGER.error("Failed to %s VPS: %s", command, data.get("message", "Unknown error"))
                        return False

                    _LOGGER.info("Successfully sent %s command to VPS %s", command, self.vps_name)
                    # Trigger a data refresh after sending a state-changing command
                    await self.async_request_refresh()
                    return True
        except Exception as err:
            _LOGGER.error("Error sending %s command to VPS: %s", command, err)
            return False
