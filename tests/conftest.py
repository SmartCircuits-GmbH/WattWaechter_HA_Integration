"""Common fixtures for WattWächter Plus tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL, CONF_TOKEN
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.wattwaechter.const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_FW_VERSION,
    CONF_MAC,
    CONF_MODEL,
    DOMAIN,
)

MOCK_HOST = "192.168.1.100"
MOCK_TOKEN = "test-token-123"
MOCK_DEVICE_ID = "ABC123"
MOCK_DEVICE_NAME = "Haushalt Test"
MOCK_MAC = "AA:BB:CC:DD:EE:FF"
MOCK_MODEL = "WW-Plus"
MOCK_FW_VERSION = "1.2.3"

MOCK_CONFIG_DATA = {
    CONF_HOST: MOCK_HOST,
    CONF_TOKEN: MOCK_TOKEN,
    CONF_DEVICE_ID: MOCK_DEVICE_ID,
    CONF_DEVICE_NAME: MOCK_DEVICE_NAME,
    CONF_MODEL: MOCK_MODEL,
    CONF_FW_VERSION: MOCK_FW_VERSION,
    CONF_MAC: MOCK_MAC,
}

MOCK_SETTINGS = {
    "device_name": MOCK_DEVICE_NAME,
    "wifi": {},
    "mqtt": {},
}

MOCK_ALIVE_RESPONSE = {
    "alive": True,
    "version": MOCK_FW_VERSION,
}

MOCK_SYSTEM_INFO = {
    "uptime": [{"name": "uptime", "value": "2d 5h 30m"}],
    "wifi": [
        {"name": "ssid", "value": "MyNetwork"},
        {"name": "signal_strength", "value": -45},
        {"name": "ip_address", "value": MOCK_HOST},
        {"name": "mac_address", "value": MOCK_MAC},
        {"name": "mdns_name", "value": "wattwaechter-aabbccddeeff.local"},
    ],
    "esp": [
        {"name": "esp_id", "value": MOCK_DEVICE_ID},
        {"name": "os_version", "value": MOCK_FW_VERSION},
    ],
    "heap": [{"name": "free_heap", "value": 120000}],
}

MOCK_METER_DATA = {
    "timestamp": 1704067200,
    "datetime": "2024-01-01T00:00:00",
    "1.8.0": {"value": 12345.678, "unit": "kWh"},
    "2.8.0": {"value": 1234.567, "unit": "kWh"},
    "16.7.0": {"value": 1500.5, "unit": "W"},
    "32.7.0": {"value": 230.1, "unit": "V"},
    "31.7.0": {"value": 6.52, "unit": "A"},
    "14.7.0": {"value": 50.01, "unit": "Hz"},
    "13.7.0": {"value": 0.985, "unit": ""},
}

MOCK_METER_DATA_MINIMAL = {
    "timestamp": 1704067200,
    "datetime": "2024-01-01T00:00:00",
    "1.8.0": {"value": 100.0, "unit": "kWh"},
    "16.7.0": {"value": 500, "unit": "W"},
}

MOCK_METER_DATA_WITH_UNKNOWN = {
    "timestamp": 1704067200,
    "datetime": "2024-01-01T00:00:00",
    "1.8.0": {"value": 12345.678, "unit": "kWh"},
    "99.99.0": {"value": 42.5, "unit": "W"},
    "0.0.0": {"value": "1EMH0012345678", "unit": ""},
}

MOCK_OTA_CHECK_NO_UPDATE = {
    "ok": True,
    "data": {
        "update_available": False,
        "version": MOCK_FW_VERSION,
    },
}

MOCK_OTA_CHECK_UPDATE = {
    "ok": True,
    "data": {
        "update_available": True,
        "version": "2.0.0",
        "release_note_en": "Bug fixes and improvements",
        "release_note_de": "Fehlerbehebungen und Verbesserungen",
    },
}


@pytest.fixture(autouse=True, scope="session")
def _warmup_pycares_thread():
    """Pre-start pycares background thread to avoid thread-leak false positive.

    pycares starts a global daemon thread (_run_safe_shutdown_loop) the first
    time a Channel is created.  If the thread starts *during* a test, the
    pytest-homeassistant-custom-component teardown detects it as a leak.
    Starting it once at session scope puts it into every test's
    ``threads_before`` snapshot.
    """
    from pycares import _shutdown_manager

    _shutdown_manager.start()


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading of custom components in all tests."""
    yield


@pytest.fixture(autouse=True)
def mock_zeroconf(hass: HomeAssistant):
    """Mock zeroconf dependency to avoid socket access in tests."""
    hass.config.components.add("zeroconf")
    yield


@pytest.fixture
def mock_api():
    """Create a mock API client."""
    with patch(
        "custom_components.wattwaechter.api.WattwaechterApiClient",
        autospec=True,
    ) as mock_cls:
        client = mock_cls.return_value
        client.host = MOCK_HOST
        client.async_alive = AsyncMock(return_value=MOCK_ALIVE_RESPONSE)
        client.async_get_system_info = AsyncMock(return_value=MOCK_SYSTEM_INFO)
        client.async_get_settings = AsyncMock(return_value=MOCK_SETTINGS)
        client.async_get_meter_data = AsyncMock(return_value=MOCK_METER_DATA)
        client.async_check_ota = AsyncMock(return_value=MOCK_OTA_CHECK_NO_UPDATE)
        client.async_start_ota = AsyncMock(return_value={"ok": True})
        yield client


@pytest.fixture
def mock_config_entry(hass: HomeAssistant):
    """Create a mock config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=MOCK_DEVICE_NAME,
        data=MOCK_CONFIG_DATA,
        source="user",
        unique_id=MOCK_DEVICE_ID,
        version=1,
    )
    entry.add_to_hass(hass)
    return entry
