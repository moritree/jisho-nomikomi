import json
import os
from pathlib import Path

import jsonpickle

CONFIG_FILENAME = 'config.json'
LIBRARY_FILENAME = 'library.json'
CACHE_DIR: Path = Path.home() / '.nomikomi'
TOKEN_CACHE_FILENAME = 'token_cache.csv'
VALID_FIELDS = ['vocab', 'kana', 'translation', 'part_of_speech', 'jlpt_level', 'example']


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


class HeaderConfig:
    def __init__(self, columns=None, deck: str = None, tags: list[str] = None):
        self.columns = columns or VALID_FIELDS
        self.deck = deck
        self.tags = tags
        self.separator = 'comma'


class Config:
    def __init__(self, header: HeaderConfig = HeaderConfig, senses: int = 1):
        self.header = HeaderConfig()
        self.senses = senses

    def save(self):
        with open(CACHE_DIR / CONFIG_FILENAME, 'w') as file:
            file.write(jsonpickle.encode(self))

    def __str__(self):
        return f'header: {self.header.__dict__},\nsenses: {self.senses}'


def get_config() -> Config:
    """Load config object. Generates default configuration if no config file exists."""
    path = CACHE_DIR / CONFIG_FILENAME
    # If there is no config file, generate a default config object
    if not os.path.isfile(path):
        return Config()

    # Otherwise load from file
    with open(path, 'r') as file:
        return jsonpickle.decode(file.read())
