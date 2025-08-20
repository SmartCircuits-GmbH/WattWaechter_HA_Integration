# config_flow.py
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class WattWaecherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    _discovered = {}

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="WattWächter", data={})

        return self.async_show_form(step_id="user")

    async def async_step_zeroconf(self, discovery_info) -> FlowResult:
        _LOGGER.debug(f"Zeroconf discovery: {discovery_info}")

        host = discovery_info["host"]
        serial = discovery_info["properties"].get("serialno")
        model = discovery_info["properties"].get("model")
        fw = discovery_info["properties"].get("fw")

        # Save discovered device in global integration state
        self.hass.data.setdefault(DOMAIN, {}).setdefault("discovered", {})[serial] = {
            "host": host,
            "serial": serial,
            "model": model,
            "fw": fw,
        }

        return self.async_abort(reason="single_instance_allowed")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WattWaecherOptionsFlowHandler(config_entry)

class WattWaecherOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        discovered = self.hass.data.get(DOMAIN, {}).get("discovered", {})

        if not discovered:
            return self.async_abort(reason="no_devices_found")

        options = [(d["serial"], f"{d['serial']} ({d['host']})") for d in discovered.values()]

        if user_input is not None:
            serial = user_input["serial"]
            device = discovered[serial]
            return self.async_create_entry(
                title=f"{serial}",
                data={CONF_HOST: device["host"]}
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("serial"): vol.In({s: l for s, l in options})
            }),
            description_placeholders={"count": str(len(discovered))}
        )
