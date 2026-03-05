"""Platform for sensor integration."""
import logging
from datetime import datetime, timezone

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfInformation
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
    """Set up the BandwagonHost sensor platform from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        KiwiVMHostnameSensor(coordinator),
        KiwiVMStatusSensor(coordinator),
        KiwiVMLoadSensor(coordinator),
        KiwiVMLoad1MinSensor(coordinator),
        KiwiVMLoad5MinSensor(coordinator),
        KiwiVMLoad15MinSensor(coordinator),
        KiwiVMDataUsageSensor(coordinator),
        KiwiVMDataLimitSensor(coordinator),
        KiwiVMDataResetSensor(coordinator),
        KiwiVMMemAvailableSensor(coordinator),
        KiwiVMMemUsageSensor(coordinator),
        KiwiVMSwapAvailableSensor(coordinator),
        KiwiVMSwapUsageSensor(coordinator),
        KiwiVMDiskQuotaSensor(coordinator),
        KiwiVMDiskUsageSensor(coordinator),
        KiwiVMIPAddressSensor(coordinator),
    ]

    async_add_entities(entities)


class KiwiVMBaseSensor(CoordinatorEntity, SensorEntity):
    """Base representation of a KiwiVM sensor."""

    def __init__(self, coordinator: KiwiVMDataUpdateCoordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.vps_name = coordinator.vps_name
        self.veid = coordinator.veid

    @property
    def _data(self):
        """Helper to get data from the coordinator."""
        return self.coordinator.data or {}


class KiwiVMHostnameSensor(KiwiVMBaseSensor):
    """Sensor for VPS Hostname."""

    @property
    def name(self):
        return f"{self.vps_name} Hostname"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_hostname"

    @property
    def state(self):
        return self._data.get("hostname", "Unknown")

    @property
    def icon(self):
        return "mdi:server"


class KiwiVMStatusSensor(KiwiVMBaseSensor):
    """Sensor for VPS Status."""

    @property
    def name(self):
        return f"{self.vps_name} Status"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_status"

    @property
    def state(self):
        if "ve_status" in self._data:
            return self._data["ve_status"]
        return "Online" if self._data.get("error") == 0 else "Offline"

    @property
    def icon(self):
        return "mdi:check-network"


class KiwiVMLoadSensor(KiwiVMBaseSensor):
    """Sensor for VPS CPU Load."""

    @property
    def name(self):
        return f"{self.vps_name} CPU Load"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_cpu_load"

    @property
    def state(self):
        return self._data.get("load_average", "Unknown")

    @property
    def icon(self):
        return "mdi:cpu-64-bit"


class KiwiVMLoad1MinSensor(KiwiVMBaseSensor):
    """Sensor for VPS CPU Load 1 Min."""

    @property
    def name(self):
        return f"{self.vps_name} CPU Load 1 Min"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_cpu_load_1m"

    @property
    def state(self):
        val = self._data.get("load_average")
        if val:
            parts = val.split()
            if len(parts) >= 1:
                return parts[0]
        return "Unknown"

    @property
    def icon(self):
        return "mdi:cpu-64-bit"


class KiwiVMLoad5MinSensor(KiwiVMBaseSensor):
    """Sensor for VPS CPU Load 5 Min."""

    @property
    def name(self):
        return f"{self.vps_name} CPU Load 5 Min"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_cpu_load_5m"

    @property
    def state(self):
        val = self._data.get("load_average")
        if val:
            parts = val.split()
            if len(parts) >= 2:
                return parts[1]
        return "Unknown"

    @property
    def icon(self):
        return "mdi:cpu-64-bit"


class KiwiVMLoad15MinSensor(KiwiVMBaseSensor):
    """Sensor for VPS CPU Load 15 Min."""

    @property
    def name(self):
        return f"{self.vps_name} CPU Load 15 Min"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_cpu_load_15m"

    @property
    def state(self):
        val = self._data.get("load_average")
        if val:
            parts = val.split()
            if len(parts) >= 3:
                return parts[2]
        return "Unknown"

    @property
    def icon(self):
        return "mdi:cpu-64-bit"


class KiwiVMDataUsageSensor(KiwiVMBaseSensor):
    """Sensor for VPS Data Usage."""

    @property
    def name(self):
        return f"{self.vps_name} Data Usage"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_data_usage"

    @property
    def state(self):
        val = self._data.get("data_counter")
        if val is not None:
            return round(float(val) / 1073741824, 2)
        return None

    @property
    def unit_of_measurement(self):
        return UnitOfInformation.GIGABYTES

    @property
    def icon(self):
        return "mdi:transfer"


class KiwiVMDataLimitSensor(KiwiVMBaseSensor):
    """Sensor for VPS Data Limit."""

    @property
    def name(self):
        return f"{self.vps_name} Data Monthly Limit"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_data_limit"

    @property
    def state(self):
        val = self._data.get("plan_monthly_data")
        if val is not None:
            return round(float(val) / 1073741824, 2)
        return None

    @property
    def unit_of_measurement(self):
        return UnitOfInformation.GIGABYTES

    @property
    def icon(self):
        return "mdi:harddisk"


class KiwiVMDataResetSensor(KiwiVMBaseSensor):
    """Sensor for VPS Data Next Reset Date."""

    @property
    def name(self):
        return f"{self.vps_name} Data Next Reset"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_data_reset"

    @property
    def device_class(self):
        return SensorDeviceClass.TIMESTAMP

    @property
    def state(self):
        val = self._data.get("data_next_reset")
        if val is not None:
            # Convert UNIX timestamp to a localized ISO format string
            # HA Timestamp sensors expect an ISO 8601 formatted string or datetime object
            dt = datetime.fromtimestamp(int(val), tz=timezone.utc)
            return dt.isoformat()
        return None

    @property
    def icon(self):
        return "mdi:calendar-clock"


class KiwiVMMemAvailableSensor(KiwiVMBaseSensor):
    """Sensor for VPS Available Memory."""

    @property
    def name(self):
        return f"{self.vps_name} Memory Available"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_memory_available"

    @property
    def state(self):
        val = self._data.get("mem_available_kb")
        if val is not None:
            return round(float(val) / 1024, 2)
        return None

    @property
    def unit_of_measurement(self):
        return UnitOfInformation.MEGABYTES

    @property
    def icon(self):
        return "mdi:memory"


class KiwiVMMemUsageSensor(KiwiVMBaseSensor):
    """Sensor for VPS Used Memory."""

    @property
    def name(self):
        return f"{self.vps_name} Memory Usage"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_memory_usage"

    @property
    def state(self):
        total_bytes = self._data.get("plan_ram")
        avail_kb = self._data.get("mem_available_kb")
        if total_bytes is not None and avail_kb is not None:
            # Calculate used RAM in MB
            used_kb = (float(total_bytes) / 1024) - float(avail_kb)
            return round(used_kb / 1024, 2)
        return None

    @property
    def unit_of_measurement(self):
        return UnitOfInformation.MEGABYTES

    @property
    def icon(self):
        return "mdi:memory"


class KiwiVMSwapAvailableSensor(KiwiVMBaseSensor):
    """Sensor for VPS Available Swap."""

    @property
    def name(self):
        return f"{self.vps_name} Swap Available"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_swap_available"

    @property
    def state(self):
        val = self._data.get("swap_available_kb")
        if val is not None:
            return round(float(val) / 1024, 2)
        return None

    @property
    def unit_of_measurement(self):
        return UnitOfInformation.MEGABYTES

    @property
    def icon(self):
        return "mdi:memory"


class KiwiVMSwapUsageSensor(KiwiVMBaseSensor):
    """Sensor for VPS Used Swap."""

    @property
    def name(self):
        return f"{self.vps_name} Swap Usage"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_swap_usage"

    @property
    def state(self):
        total_kb = self._data.get("swap_total_kb")
        avail_kb = self._data.get("swap_available_kb")
        if total_kb is not None and avail_kb is not None:
            used_kb = float(total_kb) - float(avail_kb)
            return round(used_kb / 1024, 2)
        return None

    @property
    def unit_of_measurement(self):
        return UnitOfInformation.MEGABYTES

    @property
    def icon(self):
        return "mdi:memory"


class KiwiVMDiskQuotaSensor(KiwiVMBaseSensor):
    """Sensor for VPS Disk Quota."""

    @property
    def name(self):
        return f"{self.vps_name} Disk Quota"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_disk_quota"

    @property
    def state(self):
        val = self._data.get("plan_disk")
        if val is not None:
            return round(float(val) / 1073741824, 2)
        return None

    @property
    def unit_of_measurement(self):
        return UnitOfInformation.GIGABYTES

    @property
    def icon(self):
        return "mdi:harddisk"


class KiwiVMDiskUsageSensor(KiwiVMBaseSensor):
    """Sensor for VPS Used Disk."""

    @property
    def name(self):
        return f"{self.vps_name} Disk Usage"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_disk_usage"

    @property
    def state(self):
        used_bytes = self._data.get("ve_used_disk_space_b")
        if used_bytes is not None:
            return round(float(used_bytes) / 1073741824, 2)
        return None

    @property
    def unit_of_measurement(self):
        return UnitOfInformation.GIGABYTES

    @property
    def icon(self):
        return "mdi:harddisk"


class KiwiVMIPAddressSensor(KiwiVMBaseSensor):
    """Sensor for VPS IP Address."""

    @property
    def name(self):
        return f"{self.vps_name} IP Address"

    @property
    def unique_id(self):
        return f"bandwagonhost_{self.veid}_ip_address"

    @property
    def state(self):
        ips = self._data.get("ip_addresses", [])
        return ips[0] if ips else "Unknown"

    @property
    def icon(self):
        return "mdi:ip-network"
