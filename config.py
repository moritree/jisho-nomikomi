import json
import os
from pathlib import Path

CONFIG_FILENAME = 'config.json'
CACHE_DIR: Path = Path.home() / '.nomikomi'
CACHE_FILENAME = 'cache.csv'
TOKEN_CACHE_FILENAME = 'token_cache.csv'


def update_settings(items: dict):
    config = read_config() or {}  # current settings
    with open(CACHE_DIR / CONFIG_FILENAME, 'w+') as file:
        for key, value in items.items():
            if key in config:
                if value is None:
                    # delete dict item
                    config.pop(key)
                else:
                    # update with new value
                    config[key] = value
            else:
                config.update({key: value})
        # write to config file
        json.dump(config, file)


def read_config() -> dict | None:
    """Returns a dictionary with config values, or None if config file does not exist."""
    if not os.path.isfile(CACHE_DIR / CONFIG_FILENAME):
        return None
    with open(CACHE_DIR / CONFIG_FILENAME, 'r+') as file:
        return json.load(file)


def get_config_value(key: str) -> str | None:
    """Returns a value from a specific key in the config file, or None if config file or key does not exist."""
    with open(CACHE_DIR / CONFIG_FILENAME, 'r') as file:
        return json.load(file).get(key)
