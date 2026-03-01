"""Firmware update platform for the WattWächter Plus integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import WattwaechterApiClient, WattwaechterAuthError, WattwaechterConnectionError
from .const import DOMAIN, OTA_CHECK_INTERVAL
from .coordinator import WattwaechterCoordinator
from .entity import WattwaechterEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WattWächter firmware update entity."""
    coordinator: WattwaechterCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WattwaechterUpdateEntity(coordinator)])


class WattwaechterUpdateEntity(WattwaechterEntity, UpdateEntity):
    """Firmware update entity for WattWächter Plus."""

    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = UpdateEntityFeature.INSTALL
    _attr_unique_id_suffix = "firmware_update"

    def __init__(self, coordinator: WattwaechterCoordinator) -> None:
        """Initialize the update entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_firmware_update"
        self._ota_data: dict[str, Any] | None = None
        self._last_check: float = 0

    @property
    def name(self) -> str:
        """Return entity name."""
        return "Firmware"

    @property
    def installed_version(self) -> str | None:
        """Return the installed firmware version."""
        return self.coordinator.fw_version or None

    @property
    def latest_version(self) -> str | None:
        """Return the latest available firmware version."""
        if self._ota_data and self._ota_data.get("update_available"):
            return self._ota_data.get("version")
        return self.installed_version

    @property
    def release_summary(self) -> str | None:
        """Return release notes."""
        if not self._ota_data or not self._ota_data.get("update_available"):
            return None
        # Try German first, fall back to English
        return (
            self._ota_data.get("release_note_de")
            or self._ota_data.get("release_note_en")
        )

    async def async_install(
        self, version: str | None, backup: bool, **kwargs: Any
    ) -> None:
        """Install a firmware update."""
        try:
            await self.coordinator.api.async_start_ota()
        except WattwaechterAuthError:
            _LOGGER.error(
                "Cannot start firmware update: WRITE API token required"
            )
            raise
        except WattwaechterConnectionError as err:
            _LOGGER.error("Cannot start firmware update: %s", err)
            raise

    async def async_update(self) -> None:
        """Check for firmware updates periodically."""
        import time

        now = time.monotonic()
        if now - self._last_check < OTA_CHECK_INTERVAL:
            return

        self._last_check = now
        try:
            result = await self.coordinator.api.async_check_ota()
            self._ota_data = result.get("data", {})
        except (WattwaechterConnectionError, WattwaechterAuthError) as err:
            _LOGGER.debug("OTA check failed: %s", err)
