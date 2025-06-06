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
    def __init__(self, hass):
        self.session = async_get_clientsession(hass)

    async def validate_grok(self, api_key: str) -> Optional[str]:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        try:
            resp = await self.session.get("https://api.x.ai/v1/models", headers=headers)
            return None if resp.status == 200 else await resp.text()
        except Exception as err:
            return str(err)

class GrokAutomationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self.data: Dict[str, Any] = {}
        self.validator: ProviderValidator | None = None

    async def async_step_user(self, user_input: Dict[str, Any] | None = None):
        errors: Dict[str, str] = {}
        if user_input:
            self.validator = ProviderValidator(self.hass)
            error = await self.validator.validate_grok(user_input[CONF_GROK_API_KEY])
            if error is None:
                self.data.update({
                    **user_input,
                    CONF_MAX_INPUT_TOKENS: user_input.get(CONF_MAX_INPUT_TOKENS, DEFAULT_MAX_INPUT_TOKENS),
                    CONF_MAX_OUTPUT_TOKENS: user_input.get(CONF_MAX_OUTPUT_TOKENS, DEFAULT_MAX_OUTPUT_TOKENS),
                })
                return self.async_create_entry(title="Grok Automation Suggester", data=self.data)
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
                description_placeholders={"error_message": error}
            )

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
        return GrokAutomationOptionsFlowHandler(config_entry)

class GrokAutomationOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._config_entry = config_entry  # Use a different attribute name to avoid deprecated behavior

    async def async_step_init(self, user_input=None):
        if user_input:
            new_data = {
                **self._config_entry.options,
                **user_input,
                CONF_MAX_INPUT_TOKENS: user_input.get(CONF_MAX_INPUT_TOKENS, self._config_entry.data.get(CONF_MAX_INPUT_TOKENS, DEFAULT_MAX_INPUT_TOKENS)),
                CONF_MAX_OUTPUT_TOKENS: user_input.get(CONF_MAX_OUTPUT_TOKENS, self._config_entry.data.get(CONF_MAX_OUTPUT_TOKENS, DEFAULT_MAX_OUTPUT_TOKENS)),
            }
            return self.async_create_entry(title="", data=new_data)

        schema = {
            vol.Optional(CONF_GROK_API_KEY): str,
            vol.Optional(CONF_GROK_MODEL, default=self._config_entry.data.get(CONF_GROK_MODEL, DEFAULT_MODELS["Grok"])): str,
            vol.Optional(CONF_MAX_INPUT_TOKENS, default=self._config_entry.data.get(CONF_MAX_INPUT_TOKENS, DEFAULT_MAX_INPUT_TOKENS)): vol.All(vol.Coerce(int), vol.Range(min=100)),
            vol.Optional(CONF_MAX_OUTPUT_TOKENS, default=self._config_entry.data.get(CONF_MAX_OUTPUT_TOKENS, DEFAULT_MAX_OUTPUT_TOKENS)): vol.All(vol.Coerce(int), vol.Range(min=100)),
        }
        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema))
