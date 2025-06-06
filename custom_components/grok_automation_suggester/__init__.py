from __future__ import annotations
import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
import voluptuous as vol
from .const import DOMAIN, SERVICE_GENERATE_SUGGESTIONS, ATTR_CUSTOM_PROMPT
from .coordinator import GrokAutomationCoordinator, SYSTEM_PROMPT  # Import SYSTEM_PROMPT

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Grok Automation Suggester from a config entry."""
    _LOGGER.debug(f"Configuring entry {entry.entry_id} with data: {entry.data}")
    coordinator = GrokAutomationCoordinator(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    async def handle_generate_suggestions(call: ServiceCall) -> None:
        """Handle the generate_suggestions service call."""
        _LOGGER.debug(f"Service call received: all_entities={call.data.get('all_entities')}, custom_prompt={call.data.get(ATTR_CUSTOM_PROMPT)}")
        try:
            coordinator.scan_all = call.data.get("all_entities", False)
            custom_prompt = call.data.get(ATTR_CUSTOM_PROMPT)
            if custom_prompt:
                coordinator.SYSTEM_PROMPT += f"\n\nCustom Prompt: {custom_prompt}"
                _LOGGER.debug(f"Custom prompt added: {custom_prompt}")
            await coordinator.async_refresh()
            _LOGGER.info("Suggestions generated successfully")
        except Exception as err:
            _LOGGER.error(f"Error generating suggestions: {str(err)}")
            raise
        finally:
            coordinator.SYSTEM_PROMPT = SYSTEM_PROMPT  # Reset using imported SYSTEM_PROMPT

    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERATE_SUGGESTIONS,
        handle_generate_suggestions,
        schema=vol.Schema({
            vol.Required("all_entities"): vol.Coerce(bool),
            vol.Optional(ATTR_CUSTOM_PROMPT): str,
        }),
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug(f"Unloading entry {entry.entry_id}")
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
