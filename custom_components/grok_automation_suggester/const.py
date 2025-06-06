"""Constants for the Grok Automation Suggester integration."""

DOMAIN = "grok_automation_suggester"
PLATFORMS = ["sensor"]
CONFIG_VERSION = 1
INTEGRATION_NAME = "Grok Automation Suggester"

# Token budgeting
CONF_MAX_INPUT_TOKENS = "max_input_tokens"
CONF_MAX_OUTPUT_TOKENS = "max_output_tokens"
DEFAULT_MAX_INPUT_TOKENS = 1000  # Increased from 500
DEFAULT_MAX_OUTPUT_TOKENS = 1000
DEFAULT_TEMPERATURE = 0.7

# Grok-specific keys
CONF_GROK_API_KEY = "grok_api_key"
CONF_GROK_MODEL = "grok-3-latest"
ENDPOINT_GROK = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODELS = {
    "Grok": "grok-beta"
}

# Service & attribute names
ATTR_CUSTOM_PROMPT = "custom_prompt"
SERVICE_GENERATE_SUGGESTIONS = "generate_suggestions"

# Provider-status sensor values
PROVIDER_STATUS_CONNECTED = "connected"
PROVIDER_STATUS_DISCONNECTED = "disconnected"
PROVIDER_STATUS_ERROR = "error"
PROVIDER_STATUS_INITIALIZING = "initializing"

# Sensor Keys
SENSOR_KEY_SUGGESTIONS = "suggestions"
SENSOR_KEY_STATUS = "status"
SENSOR_KEY_INPUT_TOKENS = "input_tokens"
SENSOR_KEY_OUTPUT_TOKENS = "output_tokens"
SENSOR_KEY_MODEL = "model"
SENSOR_KEY_LAST_ERROR = "last_error"
