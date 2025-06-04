from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from datetime import timedelta
import logging

DOMAIN = "wattwaechter"

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data["host"]

    async def async_fetch_data():
        session = async_get_clientsession(hass)
        url = f"http://{host}/api/meterValues"
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Unexpected status: {response.status}")
                raw = await response.json()

                # Umwandeln in flaches Dict wie {"1.8.0": 485.0, ...}
                values = {
                    item["ObisCode"]: float(item["Value"])
                    for item in raw.get("MeterValues", [])
                }

                return values
        except Exception as e:
            raise UpdateFailed(f"Data fetch failed: {e}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="wattwaechter",
        update_method=async_fetch_data,
        update_interval=timedelta(seconds=30),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True