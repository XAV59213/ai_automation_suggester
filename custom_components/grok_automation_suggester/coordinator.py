from __future__ import annotations
from datetime import datetime
import logging
import random
import re
from pathlib import Path
import yaml
import anyio
from homeassistant.components import persistent_notification
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar, device_registry as dr, entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import (
    DOMAIN,
    CONF_GROK_API_KEY,
    CONF_GROK_MODEL,
    ENDPOINT_GROK,
    CONF_MAX_INPUT_TOKENS,
    CONF_MAX_OUTPUT_TOKENS,
    DEFAULT_MAX_INPUT_TOKENS,
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_MODELS,
    SENSOR_KEY_STATUS,
    PROVIDER_STATUS_CONNECTED,
    PROVIDER_STATUS_DISCONNECTED,
    PROVIDER_STATUS_ERROR,
    PROVIDER_STATUS_INITIALIZING,
)

_LOGGER = logging.getLogger(__name__)
YAML_RE = re.compile(r"```yaml\s*([\s\S]+?)\s*```", flags=re.IGNORECASE)
SYSTEM_PROMPT = """Salut, je suis Grok, créé par xAI ! 😎 Je génère des automatisations Home Assistant basées sur tes entités, avec une touche d'humour. Analyse les entités fournies, propose des automatisations YAML en utilisant les vrais entity_ids, et adapte-toi à tout thème précisé. Go ! 🚀"""

class GrokAutomationCoordinator(DataUpdateCoordinator):
    """Coordinator for Grok Automation Suggester."""
    def __init__(self, hass: HomeAssistant, entry):
        """Initialize the coordinator."""
        self.hass = hass
        self.entry = entry
        self.previous_entities: dict[str, dict] = {}
        self.last_update: datetime | None = None
        self.SYSTEM_PROMPT = SYSTEM_PROMPT
        self.scan_all = False
        self.selected_domains: list[str] = []
        self.entity_limit = 20  # Réduit pour limiter la taille du prompt
        self.automation_read_file = True
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=None)
        self.session = async_get_clientsession(hass)
        self._last_error: str | None = None
        self.data: dict = {
            "suggestions": "No suggestions yet",
            "description": "",
            "yaml_block": "",
            "last_update": None,
            "entities_processed": [],
            "provider": "Grok",
            "last_error": "",
            SENSOR_KEY_STATUS: PROVIDER_STATUS_INITIALIZING,
        }
        self.device_registry: dr.DeviceRegistry | None = None
        self.entity_registry: er.EntityRegistry | None = None
        self.area_registry: ar.AreaRegistry | None = None

    def _opt(self, key: str, default=None):
        """Get configuration option or default value."""
        return self.entry.options.get(key, self.entry.data.get(key, default))

    def _budgets(self) -> tuple[int, int]:
        """Get input and output token budgets."""
        out_budget = self._opt(CONF_MAX_OUTPUT_TOKENS, DEFAULT_MAX_OUTPUT_TOKENS)
        in_budget = self._opt(CONF_MAX_INPUT_TOKENS, DEFAULT_MAX_INPUT_TOKENS)
        return in_budget, out_budget

    async def async_added_to_hass(self):
        """Handle coordinator added to Home Assistant."""
        await super().async_added_to_hass()
        self.device_registry = dr.async_get(self.hass)
        self.entity_registry = er.async_get(self.hass)
        self.area_registry = ar.async_get(self.hass)

    async def async_shutdown(self):
        """Handle coordinator shutdown."""
        return

    async def _async_update_data(self) -> dict:
        """Update data and generate suggestions."""
        _LOGGER.debug("Starting data update")
        try:
            now = datetime.now()
            self.last_update = now
            self._last_error = None
            current: dict[str, dict] = {}
            for eid in self.hass.states.async_entity_ids():
                if self.selected_domains and eid.split(".")[0] not in self.selected_domains:
                    continue
                st = self.hass.states.get(eid)
                if st:
                    current[eid] = {
                        "state": st.state,
                        "attributes": st.attributes,
                        "last_changed": st.last_changed,
                        "last_updated": st.last_updated,
                        "friendly_name": st.attributes.get("friendly_name", eid),
                    }
            picked = current if self.scan_all else {k: v for k, v in current.items() if k not in self.previous_entities}
            if not picked:
                _LOGGER.debug("No new entities to process")
                self.previous_entities = current
                self.data[SENSOR_KEY_STATUS] = PROVIDER_STATUS_CONNECTED
                return self.data
            prompt = await self._build_prompt(picked)
            _LOGGER.debug(f"Generated prompt length: {len(prompt)}")
            response = await self._grok(prompt)
            if response:
                _LOGGER.debug(f"Received response: {response[:200]}...")
                match = YAML_RE.search(response)
                yaml_block = match.group(1).strip() if match else ""
                description = YAML_RE.sub("", response).strip() if match else ""
                # Créer une notification persistante
                persistent_notification.async_create(
                    self.hass,
                    message=response,
                    title="Grok Automation Suggestions",
                    notification_id=f"grok_automation_suggestions_{now.timestamp()}",
                )
                # Écrire les suggestions dans un fichier
                suggestions_data = {
                    "timestamp": now.isoformat(),
                    "suggestions": response,
                    "description": description,
                    "yaml_block": yaml_block,
                    "entities_processed": list(picked.keys()),
                }
                suggestions_file = Path(self.hass.config.path("grok_suggestions.yaml"))
                try:
                    async with await anyio.open_file(suggestions_file, "w", encoding="utf-8") as file:
                        await file.write(yaml.safe_dump(suggestions_data, allow_unicode=True))
                    _LOGGER.debug(f"Suggestions written to {suggestions_file}")
                except Exception as err:
                    _LOGGER.error(f"Failed to write suggestions to {suggestions_file}: {err}")
                self.data = {
                    "suggestions": response,
                    "description": description,
                    "yaml_block": yaml_block,
                    "last_update": now,
                    "entities_processed": list(picked.keys()),
                    "provider": "Grok",
                    "last_error": "",
                    SENSOR_KEY_STATUS: PROVIDER_STATUS_CONNECTED,
                }
            else:
                _LOGGER.warning("No response from Grok API")
                self.data.update(
                    {
                        "suggestions": "No suggestions available",
                        "description": "",
                        "yaml_block": "",
                        "last_update": now,
                        "entities_processed": [],
                        "last_error": self._last_error or "No response from API",
                        SENSOR_KEY_STATUS: PROVIDER_STATUS_DISCONNECTED,
                    }
                )
            self.previous_entities = current
            return self.data
        except Exception as err:
            self._last_error = str(err)
            _LOGGER.error(f"Coordinator fatal error: {str(err)}")
            self.data.update(
                {
                    "suggestions": "Error occurred",
                    "description": "",
                    "yaml_block": "",
                    "last_update": now,
                    "entities_processed": [],
                    "last_error": self._last_error,
                    SENSOR_KEY_STATUS: PROVIDER_STATUS_ERROR,
                }
            )
            return self.data

    async def _build_prompt(self, entities: dict) -> str:
        """Build the prompt for Grok API."""
        _LOGGER.debug(f"Building prompt for {len(entities)} entities")
        MAX_ATTR = 200  # Réduit pour limiter la taille des attributs
        MAX_AUTOM = 5   # Réduit pour limiter les automatisations
        ent_sections: list[str] = []
        for eid, meta in random.sample(list(entities.items()), min(len(entities), self.entity_limit)):
            domain = eid.split(".")[0]
            attr_str = str(meta["attributes"])
            if len(attr_str) > MAX_ATTR:
                attr_str = f"{attr_str[:MAX_ATTR]}..."
            ent_entry = self.entity_registry.async_get(eid) if self.entity_registry else None
            dev_entry = self.device_registry.async_get(ent_entry.device_id) if ent_entry and ent_entry.device_id else None
            area_id = ent_entry.area_id if ent_entry and ent_entry.area_id else (dev_entry.area_id if dev_entry else None)
            area_name = "Unknown Area"
            if area_id and self.area_registry:
                ar_entry = self.area_registry.async_get_area(area_id)
                if ar_entry:
                    area_name = ar_entry.name
            block = (
                f"Entity: {eid}\n"
                f"Friendly Name: {meta['friendly_name']}\n"
                f"Domain: {domain}\n"
                f"State: {meta['state']}\n"
                f"Attributes: {attr_str}\n"
                f"Area: {area_name}\n"
                "---\n"
            )
            ent_sections.append(block)
        if self.automation_read_file:
            autom_sections = self._read_automations_default(MAX_AUTOM, MAX_ATTR)
            autom_codes = await self._read_automations_file_method(MAX_AUTOM, MAX_ATTR)
            builded_prompt = (
                f"{self.SYSTEM_PROMPT}\n\n"
                f"Entities (sampled):\n{''.join(ent_sections)}\n"
                "Existing Automations:\n"
                f"{''.join(autom_sections) if autom_sections else 'None found.'}\n\n"
                "Automations YAML:\n"
                f"{''.join(autom_codes) if autom_codes else 'None available.'}\n\n"
                "Propose new automations or improvements using the entity_ids above."
            )
        else:
            autom_sections = self._read_automations_default(MAX_AUTOM, MAX_ATTR)
            builded_prompt = (
                f"{self.SYSTEM_PROMPT}\n\n"
                f"Entities (sampled):\n{''.join(ent_sections)}\n"
                "Existing Automations:\n"
                f"{''.join(autom_sections) if autom_sections else 'None found.'}\n\n"
                "Propose new automations using the entity_ids above."
            )
        _LOGGER.debug(f"Prompt built, length: {len(builded_prompt)}")
        return builded_prompt

    def _read_automations_default(self, max_autom: int, max_attr: int) -> list[str]:
        """Read default automations from Home Assistant."""
        _LOGGER.debug(f"Reading default automations, max={max_autom}")
        automations: list[str] = []
        for aid in self.hass.states.async_entity_ids("automation")[:max_autom]:
            st = self.hass.states.get(aid)
            if st:
                attr = str(st.attributes)
                if len(attr) > max_attr:
                    attr = f"{attr[:max_attr]}...(truncated)"
                automations.append(
                    f"Entity: {aid}\n"
                    f"Friendly Name: {st.attributes.get('friendly_name', aid)}\n"
                    f"State: {st.state}\n"
                    f"Attributes: {attr}\n"
                    "---\n"
                )
        return automations

    async def _read_automations_file_method(self, max_autom: int, max_attr: int) -> list[str]:
        """Read automations from automations.yaml file."""
        _LOGGER.debug(f"Reading automations from file, max={max_autom}")
        automations_file = Path(self.hass.config.path()) / "automations.yaml"
        autom_codes: list[str] = []
        max_autom = min(max_autom, 5)
        try:
            async with await anyio.open_file(automations_file, "r", encoding="utf-8") as file:
                content = await file.read()
                automations = yaml.safe_load(content) or []
            for automation in automations[:max_autom]:
                aid = automation.get("id", "unknown_id")
                alias = automation.get("alias", "Unnamed Automation")
                description = automation.get("description", "")
                trigger = automation.get("trigger", []) or automation.get("triggers", [])
                condition = automation.get("condition", []) or automation.get("conditions", [])
                action = automation.get("action", []) or automation.get("actions", {})
                code_block = (
                    f"Automation Code for automation.{aid}:\n"
                    "```yaml\n"
                    f"- id: '{aid}'\n"
                    f"  alias: {alias}\n"
                    f"  description: {description}\n"
                    f"  trigger: {trigger}\n"
                    f"  condition: {condition}\n"
                    f"  action: {action}\n"
                    "```\n"
                    "---\n"
                )
                autom_codes.append(code_block)
        except FileNotFoundError:
            _LOGGER.error("The automations.yaml file was not found.")
        except yaml.YAMLError as err:
            _LOGGER.error(f"Error parsing automations.yaml: {err}")
        return autom_codes

    async def _grok(self, prompt: str) -> str | None:
        """Send request to Grok API and return response."""
        _LOGGER.debug(f"Sending request to Grok API with prompt length: {len(prompt)}")
        try:
            api_key = self._opt(CONF_GROK_API_KEY)
            model = self._opt(CONF_GROK_MODEL, DEFAULT_MODELS["Grok"])
            in_budget, out_budget = self._budgets()
            if not api_key:
                raise ValueError("Grok API key not configured")
            if len(prompt) // 4 > in_budget:
                _LOGGER.debug(f"Prompt truncated to fit input budget: {in_budget * 4}")
                prompt = prompt[:in_budget * 4]
            body = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": out_budget,
                "temperature": DEFAULT_TEMPERATURE,
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            _LOGGER.debug(f"Request headers: {headers}, body: {body}")
            async with self.session.post(ENDPOINT_GROK, headers=headers, json=body) as resp:
                _LOGGER.debug(f"API response status: {resp.status}")
                if resp.status != 200:
                    error_text = await resp.text()
                    self._last_error = f"Grok error {resp.status}: {error_text}"
                    _LOGGER.error(self._last_error)
                    return None
                res = await resp.json()
                _LOGGER.debug(f"API response: {res}")
                if not isinstance(res, dict) or "choices" not in res or not res["choices"] or "message" not in res["choices"][0] or "content" not in res["choices"][0]["message"]:
                    raise ValueError(f"Unexpected response format: {res}")
                return res["choices"][0]["message"]["content"]
        except Exception as err:
            self._last_error = f"Grok processing error: {str(err)}"
            _LOGGER.error(self._last_error)
            return None
