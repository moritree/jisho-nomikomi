import json
from pathlib import Path

CONFIG_FILENAME = 'config.json'
CACHE_DIR: Path = Path.home() / '.nomikomi'
CACHE_FILENAME = 'cache.csv'
TOKEN_CACHE_FILENAME = 'token_cache.csv'


def update_settings(items: dict):
    config = read_config()
    with open(CACHE_DIR / CONFIG_FILENAME, 'w') as file:
        for key, value in items.items():
            if key in config:
                config[key] = value
            else:
                config.update({key: value})
        json.dump(config, file)


def read_config():
    with open(CACHE_DIR / CONFIG_FILENAME, 'r') as file:
        return json.load(file)
