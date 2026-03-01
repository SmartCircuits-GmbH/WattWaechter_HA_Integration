"""Diagnostics support for the WattWächter Plus integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import WattwaechterCoordinator

REDACT_KEYS = {CONF_TOKEN}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: WattwaechterCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Redact sensitive data from config
    config_data = dict(entry.data)
    for key in REDACT_KEYS:
        if key in config_data and config_data[key]:
            config_data[key] = "**REDACTED**"

    return {
        "config": config_data,
        "options": dict(entry.options),
        "coordinator_data": {
            "meter": coordinator.data.meter if coordinator.data else None,
            "system": coordinator.data.system if coordinator.data else None,
        },
        "device_info": {
            "device_id": coordinator.device_id,
            "model": coordinator.model,
            "fw_version": coordinator.fw_version,
            "mac": coordinator.mac,
            "host": coordinator.host,
        },
    }
