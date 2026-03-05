"""Platform for switch integration."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import KiwiVMDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BandwagonHost switch platform from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        KiwiVMPowerSwitch(coordinator)
    ]

    async_add_entities(entities)


class KiwiVMPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a VPS Power Switch."""

    def __init__(self, coordinator: KiwiVMDataUpdateCoordinator):
        """Initialize the switch."""
        super().__init__(coordinator)
        self.vps_name = coordinator.vps_name
        self.veid = coordinator.veid

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{self.vps_name} Power Control"

    @property
    def unique_id(self):
        """Return a unique identifier for this switch."""
        return f"bandwagonhost_{self.veid}_power_switch"

    @property
    def is_on(self) -> bool:
        """Return True if the VPS is running."""
        data = self.coordinator.data or {}
        # Status can be "Running" or "Online" (sometimes dependent on the API phase)
        status = data.get("ve_status", "")
        return status in ["Running", "Online", "running", "online"]

    @property
    def icon(self):
        """Return the icon of the switch."""
        return "mdi:server-network" if self.is_on else "mdi:server-network-off"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the VPS on."""
        _LOGGER.debug("Sending start command to %s", self.vps_name)
        await self.coordinator.async_send_command("start")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the VPS off."""
        _LOGGER.debug("Sending stop command to %s", self.vps_name)
        await self.coordinator.async_send_command("stop")
