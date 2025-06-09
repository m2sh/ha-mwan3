"""The MWAN3 integration."""
from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import Any, Dict, Optional

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL,
    CONF_NAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .auth import MWAN3Auth

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the MWAN3 sensor from a config entry."""
    coordinator = MWAN3Coordinator(
        hass,
        config_entry.data[CONF_HOST],
        config_entry.data[CONF_USERNAME],
        config_entry.data[CONF_PASSWORD],
        config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        config_entry.data.get(CONF_NAME, f"MWAN3 {config_entry.data[CONF_HOST]}"),
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            MWAN3InterfaceSensor(coordinator, interface)
            for interface in coordinator.data.keys()
        ]
    )

class MWAN3Coordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        username: str,
        password: str,
        scan_interval: int,
        friendly_name: str,
    ) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=friendly_name,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.auth = MWAN3Auth(host, username, password)
        self.friendly_name = friendly_name

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from MWAN3 API."""
        try:
            headers = await self.auth.get_headers()
            # Add timestamp to prevent caching
            timestamp = int(time.time() * 1000)
            status_url = f"http://{self.auth.host}/cgi-bin/luci/admin/status/mwan/interface_status?{timestamp}"
            
            session = await self.auth._get_session()
            async with session as session:
                async with session.get(status_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_status(data)
                    else:
                        _LOGGER.error("Failed to fetch MWAN3 status: %s", response.status)
                        return {}
        except Exception as e:
            _LOGGER.error("Error fetching status: %s", str(e))
            return {}

    def _parse_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the JSON response to extract interface status."""
        interfaces = {}
        
        if "interfaces" in data:
            for name, interface in data["interfaces"].items():
                interfaces[name] = {
                    "status": interface.get("status", "unknown"),
                    "enabled": interface.get("enabled", False),
                    "score": interface.get("score", 0),
                    "up": interface.get("up", False),
                    "age": interface.get("age", 0),
                    "turn": interface.get("turn", 0),
                    "online": interface.get("online", 0),
                    "uptime": interface.get("uptime", 0),
                    "lost": interface.get("lost", 0),
                    "offline": interface.get("offline", 0),
                    "running": interface.get("running", False),
                    "track_ip": interface.get("track_ip", []),
                }
        
        return interfaces

    async def async_shutdown(self):
        """Shutdown the coordinator."""
        await self.auth.close()
        await super().async_shutdown()

class MWAN3InterfaceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a MWAN3 interface sensor."""

    def __init__(self, coordinator: MWAN3Coordinator, interface_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._interface_name = interface_name
        self._attr_name = f"{coordinator.friendly_name} {interface_name}"
        self._attr_unique_id = f"mwan3_{interface_name}"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        interface_data = self.coordinator.data.get(self._interface_name, {})
        return interface_data.get("status", "unknown")

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        interface_data = self.coordinator.data.get(self._interface_name, {})
        return {
            "enabled": interface_data.get("enabled", False),
            "score": interface_data.get("score", 0),
            "up": interface_data.get("up", False),
            "age": interface_data.get("age", 0),
            "turn": interface_data.get("turn", 0),
            "online": interface_data.get("online", 0),
            "uptime": interface_data.get("uptime", 0),
            "lost": interface_data.get("lost", 0),
            "offline": interface_data.get("offline", 0),
            "running": interface_data.get("running", False),
            "track_ip": interface_data.get("track_ip", []),
        } 