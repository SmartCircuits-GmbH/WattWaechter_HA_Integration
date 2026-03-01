"""Base entity for the WattWächter Plus integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEVICE_NAME, DOMAIN, MANUFACTURER
from .coordinator import WattwaechterCoordinator


class WattwaechterEntity(CoordinatorEntity[WattwaechterCoordinator]):
    """Base entity for WattWächter Plus devices."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: WattwaechterCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.device_id)},
            name=DEVICE_NAME,
            manufacturer=MANUFACTURER,
            model=self.coordinator.model,
            sw_version=self.coordinator.fw_version,
            configuration_url=f"http://{self.coordinator.host}",
        )
        if self.coordinator.mac:
            info["connections"] = {
                (CONNECTION_NETWORK_MAC, self.coordinator.mac)
            }
        return info
