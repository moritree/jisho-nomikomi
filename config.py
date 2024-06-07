import json
import os
from pathlib import Path

CONFIG_FILENAME = 'config.json'
LIBRARY_FILENAME = 'library.json'
CACHE_DIR: Path = Path.home() / '.nomikomi'
TOKEN_CACHE_FILENAME = 'token_cache.csv'


def update_json(items: dict, path: Path):
    loaded_dict = load_json(path) or {}  # current settings
    with open(path, 'w+') as file:
        for key, value in items.items():
            if key in loaded_dict:
                if value is None:
                    # delete dict item
                    loaded_dict.pop(key)
                else:
                    # update with new value
                    loaded_dict[key] = value
            else:
                loaded_dict.update({key: value})
        # write to config file
        json.dump(loaded_dict, file)


def load_json(path: Path) -> dict | None:
    """Returns a dictionary, or None if the file does not exist."""
    if not os.path.isfile(path):
        return None
    with open(path, 'r') as file:
        return json.load(file)
