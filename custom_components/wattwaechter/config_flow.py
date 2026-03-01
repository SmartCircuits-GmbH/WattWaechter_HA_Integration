"""Config flow for the WattWächter Plus integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL, CONF_TOKEN
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

if TYPE_CHECKING:
    from homeassistant.components.zeroconf import ZeroconfServiceInfo

from .api import WattwaechterApiClient, WattwaechterAuthError, WattwaechterConnectionError
from .const import (
    CONF_DEVICE_ID,
    CONF_FW_VERSION,
    CONF_MAC,
    CONF_MODEL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


def _has_mqtt_entities(hass: HomeAssistant, device_id: str) -> bool:
    """Check if MQTT discovery entities already exist for this device.

    The ESP publishes MQTT discovery with unique_ids like
    "wattwaechter_{device_id}_{obis}" or "WWP-{device_id}_{obis}".
    If such entities exist, the device is already integrated via MQTT.
    """
    registry = er.async_get(hass)
    prefixes = (f"wattwaechter_{device_id}_", f"WWP-{device_id}_")
    return any(
        any(entity.unique_id.startswith(p) for p in prefixes)
        for entity in registry.entities.values()
        if entity.platform == "mqtt"
    )


class WattwaechterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WattWächter Plus."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._host: str | None = None
        self._device_id: str | None = None
        self._model: str | None = None
        self._fw_version: str | None = None
        self._mac: str | None = None

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle zeroconf discovery."""
        _LOGGER.debug("Zeroconf discovery: %s", discovery_info)

        self._host = str(discovery_info.host)

        # Extract TXT record properties
        properties = discovery_info.properties
        device_id_raw = properties.get("id", "")
        self._model = properties.get("model", "WW-Plus")
        self._fw_version = properties.get("ver", "")
        self._mac = properties.get("mac", "")

        # Device ID: strip "WWP-" prefix if present
        self._device_id = device_id_raw.removeprefix("WWP-")

        if not self._device_id:
            return self.async_abort(reason="no_device_id")

        # Check if already configured, update host if IP changed
        await self.async_set_unique_id(self._device_id)
        self._abort_if_unique_id_configured(updates={CONF_HOST: self._host})

        # Verify device is reachable
        session = async_get_clientsession(self.hass)
        api = WattwaechterApiClient(self._host, session)
        try:
            await api.async_alive()
        except WattwaechterConnectionError:
            return self.async_abort(reason="cannot_connect")

        # Check if device is already registered via MQTT discovery
        if _has_mqtt_entities(self.hass, self._device_id):
            return self.async_abort(reason="already_configured_mqtt")

        self.context["title_placeholders"] = {"name": f"WattWächter {self._device_id}"}
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm zeroconf discovery."""
        errors: dict[str, str] = {}

        if user_input is not None:
            token = user_input.get(CONF_TOKEN) or None

            # Validate token if provided
            if token:
                session = async_get_clientsession(self.hass)
                api = WattwaechterApiClient(self._host, session, token)
                try:
                    await api.async_get_system_info()
                except WattwaechterAuthError:
                    errors["base"] = "invalid_auth"
                except WattwaechterConnectionError:
                    errors["base"] = "cannot_connect"

            if not errors:
                return self.async_create_entry(
                    title=f"WattWächter {self._device_id}",
                    data={
                        CONF_HOST: self._host,
                        CONF_TOKEN: token,
                        CONF_DEVICE_ID: self._device_id,
                        CONF_MODEL: self._model,
                        CONF_FW_VERSION: self._fw_version,
                        CONF_MAC: self._mac,
                    },
                )

        return self.async_show_form(
            step_id="zeroconf_confirm",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_TOKEN): str,
                }
            ),
            description_placeholders={
                "model": self._model or "WattWächter Plus",
                "firmware": self._fw_version or "unknown",
                "host": self._host or "",
                "device_id": self._device_id or "",
            },
            errors=errors,
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            token = user_input.get(CONF_TOKEN) or None

            session = async_get_clientsession(self.hass)
            api = WattwaechterApiClient(host, session, token)

            # Step 1: Check connectivity
            try:
                alive = await api.async_alive()
            except WattwaechterConnectionError:
                errors["base"] = "cannot_connect"
            else:
                fw_version = alive.get("version", "")

                # Step 2: Get device info (needs auth if enabled)
                device_id = None
                mac = ""
                model = "WW-Plus"
                try:
                    system_info = await api.async_get_system_info()
                    for item in system_info.get("esp", []):
                        if item.get("name") == "esp_id":
                            device_id = item.get("value")
                        if item.get("name") == "os_version":
                            fw_version = item.get("value", fw_version)
                    for item in system_info.get("wifi", []):
                        if item.get("name") == "mac_address":
                            mac = item.get("value", "")
                except WattwaechterAuthError:
                    errors["base"] = "invalid_auth"
                except WattwaechterConnectionError:
                    # System info failed but alive worked - might be auth issue
                    errors["base"] = "cannot_connect"

                if not errors and not device_id:
                    errors["base"] = "cannot_connect"

                if not errors:
                    # Check if device is already registered via MQTT discovery
                    if _has_mqtt_entities(self.hass, device_id):
                        return self.async_abort(reason="already_configured_mqtt")

                    await self.async_set_unique_id(device_id)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"WattWächter {device_id}",
                        data={
                            CONF_HOST: host,
                            CONF_TOKEN: token,
                            CONF_DEVICE_ID: device_id,
                            CONF_MODEL: model,
                            CONF_FW_VERSION: fw_version,
                            CONF_MAC: mac,
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_TOKEN): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow handler."""
        return WattwaechterOptionsFlow()


class WattwaechterOptionsFlow(OptionsFlow):
    """Handle options flow for WattWächter Plus."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage integration options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=current_interval,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    ),
                }
            ),
        )
