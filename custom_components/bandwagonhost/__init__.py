"""The BandwagonHost (KiwiVM) integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import HomeAssistant

from .const import CONF_API_KEY, CONF_VEID, DOMAIN
from .coordinator import KiwiVMDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# List of integration platforms we are supporting
PLATFORMS = [Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BandwagonHost from a config entry (created via UI)."""
    hass.data.setdefault(DOMAIN, {})

    name = entry.data[CONF_NAME]
    veid = entry.data[CONF_VEID]
    api_key = entry.data[CONF_API_KEY]

    _LOGGER.debug("Setting up BandwagonHost instance: %s (VEID: %s)", name, veid)

    # Create the data coordinator for this instance
    coordinator = KiwiVMDataUpdateCoordinator(
        hass,
        name=name,
        veid=veid,
        api_key=api_key,
    )

    # Fetch initial data to ensure the credentials work right away
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator for platforms to use
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to the individual platforms (sensor.py, switch.py)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
