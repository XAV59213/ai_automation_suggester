from __future__ import annotations
import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, SERVICE_GENERATE_SUGGESTIONS, ATTR_CUSTOM_PROMPT
from .coordinator import GrokAutomationCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Grok Automation Suggester from a config entry."""
    coordinator = GrokAutomationCoordinator(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    async def handle_generate_suggestions(call: ServiceCall) -> None:
        """Handle the generate_suggestions service call."""
        coordinator.scan_all = call.data.get("all_entities", False)
        custom_prompt = call.data.get(ATTR_CUSTOM_PROMPT)
        if custom_prompt:
            coordinator.SYSTEM_PROMPT += f"\n\nCustom Prompt: {custom_prompt}"
        await coordinator.async_refresh()
        coordinator.SYSTEM_PROMPT = coordinator.__class__.SYSTEM_PROMPT  # Reset prompt

    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERATE_SUGGESTIONS,
        handle_generate_suggestions,
        schema=cv.make_entity_service_schema({
            cv.Required("all_entities"): cv.boolean,
            cv.Optional(ATTR_CUSTOM_PROMPT): cv.string,
        }),
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
