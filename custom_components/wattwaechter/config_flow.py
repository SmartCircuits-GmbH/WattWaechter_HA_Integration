
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_HOST
from homeassistant.components.zeroconf import ZeroconfServiceInfo
from . import DOMAIN


class WattwaechterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=f"Wattwächter ({user_input[CONF_HOST]})", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=config_entries.vol.Schema({CONF_HOST: str}),
        )

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo) -> FlowResult:
        host = discovery_info.host
        serial = discovery_info.properties.get("serialno")
        await self.async_set_unique_id(serial or host)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})
        self.context["host"] = host
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=f"Wattwächter ({self.context['host']})", data={CONF_HOST: self.context['host']})

        return self.async_show_form(step_id="confirm")

