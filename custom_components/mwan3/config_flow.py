"""Config flow for MWAN3 integration."""
from __future__ import annotations

import logging
import time
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL,
    CONF_NAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, MIN_SCAN_INTERVAL
from .auth import MWAN3Auth

_LOGGER = logging.getLogger(__name__)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    auth = MWAN3Auth(data[CONF_HOST], data[CONF_USERNAME], data[CONF_PASSWORD])
    
    # First validate the connection
    headers = await auth.get_headers()
    timestamp = int(time.time() * 1000)
    status_url = f"http://{data[CONF_HOST]}/cgi-bin/luci/admin/status/mwan/interface_status?{timestamp}"
    
    session = await auth._get_session()
    async with session as session:
        async with session.get(status_url, headers=headers) as response:
            if response.status != 200:
                raise ValueError("cannot_connect")
            
            response_data = await response.json()
            if "interfaces" not in response_data:
                raise ValueError("invalid_response")
            
            # Get list of interface names
            interfaces = list(response_data["interfaces"].keys())
            if not interfaces:
                raise ValueError("no_interfaces")
            
            return {
                "title": data.get(CONF_NAME, f"MWAN3 {data[CONF_HOST]}"),
                "interfaces": interfaces
            }

class MWAN3ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MWAN3."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        **user_input,
                        CONF_NAME: user_input.get(CONF_NAME, f"MWAN3 {user_input[CONF_HOST]}")
                    },
                    description=f"Found interfaces: {', '.join(info['interfaces'])}"
                )
            except ValueError as err:
                errors["base"] = str(err)
            except Exception as err:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_NAME, default="MWAN3 Router"): str,
                    vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL)
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @config_entries.callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return MWAN3OptionsFlow(config_entry)

class MWAN3OptionsFlow(config_entries.OptionsFlow):
    """Handle MWAN3 options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize MWAN3 options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage MWAN3 options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                },
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL)
                    ),
                }
            ),
        ) 