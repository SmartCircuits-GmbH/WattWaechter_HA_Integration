# __init__.py
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # Initialisiere die Liste entdeckter, aber nicht hinzugefügter Geräte
    hass.data[DOMAIN].setdefault("discovered", {})

    # Wenn Config-Entry Gerätedaten enthält, setze Koordinator auf
    if CONF_HOST in entry.data:
        host = entry.data[CONF_HOST]
        session = async_get_clientsession(hass)

        async def async_fetch_data():
            url = f"http://{host}/api/meterValues"
            try:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Unexpected status: {response.status}")
                    raw = await response.json()
                    return {
                        item["ObisCode"]: float(item["Value"])
                        for item in raw.get("MeterValues", [])
                    }
            except Exception as e:
                raise UpdateFailed(f"Data fetch failed: {e}")

        update_interval = timedelta(seconds=entry.options.get(CONF_SCAN_INTERVAL, 30))

        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name="wattwaechter",
            update_method=async_fetch_data,
            update_interval=update_interval,
        )

        await coordinator.async_config_entry_first_refresh()

        hass.data[DOMAIN][entry.entry_id] = coordinator
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "sensor"))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
