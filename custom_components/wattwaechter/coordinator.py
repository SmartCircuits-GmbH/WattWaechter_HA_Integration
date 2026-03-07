"""DataUpdateCoordinator for the WattWächter Plus integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WattwaechterApiClient, WattwaechterAuthError, WattwaechterConnectionError
from .const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_FW_VERSION,
    CONF_MAC,
    CONF_MODEL,
    DEFAULT_SCAN_INTERVAL,
    DEVICE_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class WattwaechterData:
    """Data class for coordinator data."""

    meter: dict[str, Any] | None
    system: dict[str, Any]


class WattwaechterCoordinator(DataUpdateCoordinator[WattwaechterData]):
    """Coordinator for WattWächter Plus data updates."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api: WattwaechterApiClient,
    ) -> None:
        """Initialize the coordinator."""
        self.api = api
        self.device_id: str = config_entry.data[CONF_DEVICE_ID]
        self.host: str = config_entry.data[CONF_HOST]
        self.model: str = config_entry.data.get(CONF_MODEL, "WW-Plus")
        self.mac: str = config_entry.data.get(CONF_MAC, "")
        self.fw_version: str = config_entry.data.get(CONF_FW_VERSION, "")
        self.device_name: str = config_entry.data.get(CONF_DEVICE_NAME, "") or DEVICE_NAME
        self.mdns_name: str = ""

        scan_interval = config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.device_id}",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.config_entry = config_entry

    async def _async_update_data(self) -> WattwaechterData:
        """Fetch data from the WattWächter device."""
        try:
            meter_data = await self.api.async_get_meter_data()
            system_info = await self.api.async_get_system_info()
        except WattwaechterAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except WattwaechterConnectionError as err:
            raise UpdateFailed(str(err)) from err

        # Update firmware version and mDNS name from live data
        if system_info:
            for item in system_info.get("esp", []):
                if item.get("name") == "os_version":
                    self.fw_version = item.get("value", self.fw_version)
                    break
            for item in system_info.get("wifi", []):
                if item.get("name") == "mdns_name":
                    self.mdns_name = item.get("value", "")
                    break

        return WattwaechterData(meter=meter_data, system=system_info)
