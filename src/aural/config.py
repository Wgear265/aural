"""Settings read from the environment and from a .env file.

XAI_API_KEY is the secret that authorizes calls to the xAI API.
Create one at https://console.x.ai and put it in .env (copy .env.example).
.env stays on your machine. It is listed in .gitignore.

AURAL_MODEL is the model id, the name xAI uses to pick a model.
The default is grok-4.7. Change it in .env when you want a different one.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when a setting required for a live API call is missing."""


@dataclass
class Settings:
    api_key: str | None
    model: str


def load_settings() -> Settings:
    """Load .env if it exists, then read the two settings we care about."""
    load_dotenv()
    model = os.getenv("AURAL_MODEL", "grok-4.7").strip() or "grok-4.7"
    key = os.getenv("XAI_API_KEY", "").strip() or None
    return Settings(api_key=key, model=model)


def require_api_key() -> Settings:
    """Return settings, or stop with a pointer to .env.example."""
    settings = load_settings()
    if not settings.api_key:
        raise ConfigError(
            "XAI_API_KEY is not set. Copy .env.example to .env and paste "
            "your key from the xAI console (https://console.x.ai)."
        )
    return settings
