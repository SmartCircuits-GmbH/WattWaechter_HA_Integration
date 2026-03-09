"""Diagnostics support for the WattWächter Plus integration."""

from __future__ import annotations

import dataclasses
from typing import Any

from homeassistant.const import CONF_TOKEN
from homeassistant.core import HomeAssistant

from . import WattwaechterConfigEntry

REDACT_KEYS = {CONF_TOKEN}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: WattwaechterConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data

    # Redact sensitive data from config
    config_data = dict(entry.data)
    for key in REDACT_KEYS:
        if key in config_data and config_data[key]:
            config_data[key] = "**REDACTED**"

    return {
        "config": config_data,
        "options": dict(entry.options),
        "coordinator_data": {
            "meter": (
                dataclasses.asdict(coordinator.data.meter)
                if coordinator.data and coordinator.data.meter
                else None
            ),
            "system": (
                dataclasses.asdict(coordinator.data.system)
                if coordinator.data
                else None
            ),
        },
        "device_info": {
            "device_id": coordinator.device_id,
            "model": coordinator.model,
            "fw_version": coordinator.fw_version,
            "mac": coordinator.mac,
            "host": coordinator.host,
        },
    }
