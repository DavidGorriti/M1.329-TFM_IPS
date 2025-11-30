import json
from pathlib import Path

class Config:
    _instance = None

    def __new__(cls, config_file="config.json"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load(config_file)
        return cls._instance

    def _load(self, config_file):
        path = Path(config_file)
        if not path.exists():
            raise FileNotFoundError(f"Config file {config_file} not found")
        with open(path, "r") as f:
            self._config = json.load(f)

    @property
    def database(self):
        return self._config.get("database", {})

    @property
    def timezone(self):
        return self._config.get("timezone", "UTC")

    @property
    def models_2d(self):
        return self._config.get("models_2d", {})

    @property
    def models_fd(self):
        return self._config.get("models_fd", {})