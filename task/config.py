import json
import os

def load_config(config_path: str = "config.json") -> dict:

    with open(config_path, 'r') as f:
        return json.load(f)

# Load config once at startup
_config = load_config()

SYSTEM_PROMPT = _config.get('system_prompt', 'You are an assistant who answers concisely and informatively.')
DIAL_ENDPOINT = _config.get('dial_endpoint', "https://ai-proxy.lab.epam.com")
API_KEY = os.getenv('DIAL_API_KEY', '')
API_VERSION = _config.get('api_version', "2024-02-15-preview")