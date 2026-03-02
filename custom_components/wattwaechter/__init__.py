"""The WattWächter Plus integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL, CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import WattwaechterApiClient, WattwaechterConnectionError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import WattwaechterCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.UPDATE]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WattWächter Plus from a config entry."""
    host = entry.data[CONF_HOST]
    token = entry.data.get(CONF_TOKEN)

    session = async_get_clientsession(hass)
    api = WattwaechterApiClient(host, session, token)

    # Verify device is reachable
    try:
        await api.async_alive()
    except WattwaechterConnectionError as err:
        raise ConfigEntryNotReady(f"Cannot connect to {host}") from err

    coordinator = WattwaechterCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Update listener for options changes (e.g. scan interval)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update - dynamically adjust coordinator interval."""
    coordinator: WattwaechterCoordinator = hass.data[DOMAIN][entry.entry_id]
    new_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    coordinator.update_interval = timedelta(seconds=new_interval)
    await coordinator.async_request_refresh()


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a WattWächter Plus config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
