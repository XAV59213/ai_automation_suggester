from __future__ import annotations
import logging
from typing import Any
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from .const import (
    DOMAIN,
    SENSOR_KEY_SUGGESTIONS,
    SENSOR_KEY_STATUS,
    SENSOR_KEY_INPUT_TOKENS,
    SENSOR_KEY_OUTPUT_TOKENS,
    SENSOR_KEY_MODEL,
    SENSOR_KEY_LAST_ERROR,
    PROVIDER_STATUS_CONNECTED,
    PROVIDER_STATUS_DISCONNECTED,
    PROVIDER_STATUS_ERROR,
    PROVIDER_STATUS_INITIALIZING,
)
from .coordinator import GrokAutomationCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = [
        GrokAutomationSuggestionsSensor(coordinator, entry),
        GrokAutomationStatusSensor(coordinator, entry),
    ]
    async_add_entities(sensors)

class GrokAutomationBaseSensor(SensorEntity):
    """Base class for Grok Automation sensors."""
    def __init__(self, coordinator: GrokAutomationCoordinator, entry):
        """Initialize the sensor."""
        super().__init__()
        self._coordinator = coordinator
        self._entry = entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Grok Automation Suggester ({entry.title})",
            "manufacturer": "xAI",
            "model": "Grok Automation",
        }

    @property
    def should_poll(self) -> bool:
        """No polling needed for coordinator-based entities."""
        return False

    async def async_added_to_hass(self):
        """Handle entity added to Home Assistant."""
        self._coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Handle entity removal from Home Assistant."""
        self._coordinator.async_remove_listener(self.async_write_ha_state)

class GrokAutomationSuggestionsSensor(GrokAutomationBaseSensor):
    """Sensor for automation suggestions."""
    def __init__(self, coordinator: GrokAutomationCoordinator, entry):
        """Initialize the suggestions sensor."""
        super().__init__(coordinator, entry)
        self._attr_name = f"{entry.title} Suggestions"
        self._attr_unique_id = f"{entry.entry_id}_suggestions"
        self._attr_icon = "mdi:robot-happy"

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        if self._coordinator.data.get("yaml_block") or self._coordinator.data.get("description"):
            return "Available"
        return "No suggestions"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "suggestions": self._coordinator.data.get(SENSOR_KEY_SUGGESTIONS, "No suggestions yet"),
            "description": self._coordinator.data.get("description"),
            "yaml_block": self._coordinator.data.get("yaml_block"),
            "last_update": str(self._coordinator.data.get("last_update")),
            "entities_processed": self._coordinator.data.get("entities_processed", []),
            "provider": self._coordinator.data.get("provider"),
        }

class GrokAutomationStatusSensor(GrokAutomationBaseSensor):
    """Sensor for provider status."""
    def __init__(self, coordinator: GrokAutomationCoordinator, entry):
        """Initialize the status sensor."""
        super().__init__(coordinator, entry)
        self._attr_name = f"{entry.title} Status"
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_icon = "mdi:connection"

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        if self._coordinator._last_error:
            return PROVIDER_STATUS_ERROR
        return PROVIDER_STATUS_CONNECTED if self._coordinator.data.get(SENSOR_KEY_STATUS) else PROVIDER_STATUS_DISCONNECTED

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        return {
            "input_tokens": self._coordinator.data.get(SENSOR_KEY_INPUT_TOKENS, 0),
            "output_tokens": self._coordinator.data.get(SENSOR_KEY_OUTPUT_TOKENS, 0),
            "model": self._coordinator.data.get(SENSOR_KEY_MODEL, ""),
            "last_error": self._coordinator.data.get(SENSOR_KEY_LAST_ERROR),
        }
