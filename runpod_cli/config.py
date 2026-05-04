"""Configuration management for RunPod CLI."""

import os
from pathlib import Path
from typing import Optional

import yaml

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "runpod-cli" / "config.yml"


class Config:
    """Handles loading and saving RunPod CLI configuration."""

    def __init__(self, path: Optional[str] = None):
        self.path = Path(path) if path else DEFAULT_CONFIG_PATH
        self._data = self._load()

    def _load(self) -> dict:
        """Load config from disk."""
        if self.path.exists():
            with open(self.path, "r") as f:
                return yaml.safe_load(f) or {}
        return {}

    def save(self):
        """Save config to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            yaml.dump(self._data, f, default_flow_style=False, sort_keys=False)
        os.chmod(self.path, 0o600)

    def get_api_key(self) -> Optional[str]:
        """Get the stored RunPod API key."""
        return self._data.get("api_key")

    def set_api_key(self, api_key: str):
        """Set the RunPod API key."""
        self._data["api_key"] = api_key
        self.save()

    def get_default_endpoint(self, endpoint_type: str) -> Optional[str]:
        """Get default endpoint ID for a given type."""
        return self._data.get("endpoints", {}).get(endpoint_type)

    def set_default_endpoint(self, endpoint_type: str, endpoint_id: str):
        """Set default endpoint ID for a given type."""
        if "endpoints" not in self._data:
            self._data["endpoints"] = {}
        self._data["endpoints"][endpoint_type] = endpoint_id
        self.save()
