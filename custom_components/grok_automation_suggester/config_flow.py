from __future__ import annotations
import logging
from typing import Any, Dict, Optional
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import (
    DOMAIN,
    CONF_GROK_API_KEY,
    CONF_GROK_MODEL,
    CONF_MAX_INPUT_TOKENS,
    CONF_MAX_OUTPUT_TOKENS,
    DEFAULT_MAX_INPUT_TOKENS,
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_MODELS,
)

_LOGGER = logging.getLogger(__name__)

class ProviderValidator:
    """Validator for Grok API key."""
    def __init__(self, hass):
        self.session = async_get_clientsession(hass)

    async def validate_grok(self, api_key: str) -> Optional[str]:
        """Validate the Grok API key by making a test request."""
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        try:
            resp = await self.session.get("https://api.x.ai/v1/models", headers=headers)
            return None if resp.status == 200 else await resp.text()
        except Exception as err:
            return str(err)

class GrokAutomationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configuration flow for Grok Automation Suggester."""
    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.data: Dict[str, Any] = {}
        self.validator: ProviderValidator | None = None

    async def async_step_user(self, user_input: Dict[str, Any] | None = None):
        """Handle the initial user input step for configuration."""
        errors: Dict[str, str] = {}
        if user_input:
            self.validator = ProviderValidator(self.hass)
            error = await self.validator.validate_grok(user_input[CONF_GROK_API_KEY])
            if error is None:
                # API key is valid, store the configuration
                self.data.update({
                    CONF_GROK_API_KEY: user_input[CONF_GROK_API_KEY],
                    CONF_GROK_MODEL: user_input.get(CONF_GROK_MODEL, DEFAULT_MODELS["Grok"]),
                    CONF_MAX_INPUT_TOKENS: user_input.get(CONF_MAX_INPUT_TOKENS, DEFAULT_MAX_INPUT_TOKENS),
                    CONF_MAX_OUTPUT_TOKENS: user_input.get(CONF_MAX_OUTPUT_TOKENS, DEFAULT_MAX_OUTPUT_TOKENS),
                })
                return self.async_create_entry(title="Grok Automation Suggester", data=self.data)
            # API key validation failed, show the error
            errors["base"] = "api_error"
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_GROK_API_KEY): str,
                    vol.Optional(CONF_GROK_MODEL, default=DEFAULT_MODELS["Grok"]): str,
                    vol.Optional(CONF_MAX_INPUT_TOKENS, default=DEFAULT_MAX_INPUT_TOKENS): vol.All(vol.Coerce(int), vol.Range(min=100)),
                    vol.Optional(CONF_MAX_OUTPUT_TOKENS, default=DEFAULT_MAX_OUTPUT_TOKENS): vol.All(vol.Coerce(int), vol.Range(min=100)),
                }),
                errors=errors,
                description_placeholders={"api_error": error or "Erreur de validation de la clé API. Vérifiez votre clé et réessayez."}
            )

        # Show the initial configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_GROK_API_KEY): str,
                vol.Optional(CONF_GROK_MODEL, default=DEFAULT_MODELS["Grok"]): str,
                vol.Optional(CONF_MAX_INPUT_TOKENS, default=DEFAULT_MAX_INPUT_TOKENS): vol.All(vol.Coerce(int), vol.Range(min=100)),
                vol.Optional(CONF_MAX_OUTPUT_TOKENS, default=DEFAULT_MAX_OUTPUT_TOKENS): vol.All(vol.Coerce(int), vol.Range(min=100)),
            }),
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return GrokAutomationOptionsFlowHandler(config_entry)

class GrokAutomationOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for updating Grok Automation Suggester configuration."""
    def __init__(self, config_entry):
        """Initialize the options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle the options configuration step."""
        if user_input:
            # Update options with new user input
            new_data = {
                CONF_GROK_API_KEY: user_input.get(CONF_GROK_API_KEY, self._config_entry.data.get(CONF_GROK_API_KEY)),
                CONF_GROK_MODEL: user_input.get(CONF_GROK_MODEL, self._config_entry.data.get(CONF_GROK_MODEL, DEFAULT_MODELS["Grok"])),
                CONF_MAX_INPUT_TOKENS: user_input.get(CONF_MAX_INPUT_TOKENS, self._config_entry.data.get(CONF_MAX_INPUT_TOKENS, DEFAULT_MAX_INPUT_TOKENS)),
                CONF_MAX_OUTPUT_TOKENS: user_input.get(CONF_MAX_OUTPUT_TOKENS, self._config_entry.data.get(CONF_MAX_OUTPUT_TOKENS, DEFAULT_MAX_OUTPUT_TOKENS)),
            }
            return self.async_create_entry(title="", data=new_data)

        # Show the options form
        schema = {
            vol.Optional(CONF_GROK_API_KEY, default=self._config_entry.data.get(CONF_GROK_API_KEY, "")): str,
            vol.Optional(CONF_GROK_MODEL, default=self._config_entry.data.get(CONF_GROK_MODEL, DEFAULT_MODELS["Grok"])): str,
            vol.Optional(CONF_MAX_INPUT_TOKENS, default=self._config_entry.data.get(CONF_MAX_INPUT_TOKENS, DEFAULT_MAX_INPUT_TOKENS)): vol.All(vol.Coerce(int), vol.Range(min=100)),
            vol.Optional(CONF_MAX_OUTPUT_TOKENS, default=self._config_entry.data.get(CONF_MAX_OUTPUT_TOKENS, DEFAULT_MAX_OUTPUT_TOKENS)): vol.All(vol.Coerce(int), vol.Range(min=100)),
        }
        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema))
