import json
import os
import jsonpickle
from pathlib import Path

from jisho_api.word.cfg import WordConfig

CONFIG_FILENAME = 'config.json'
LIBRARY_FILENAME = 'library.json'
CACHE_DIR: Path = Path.home() / '.nomikomi'
TOKEN_CACHE_FILENAME = 'token_cache.csv'
VALID_FIELDS = ['vocab', 'kana', 'translation', 'part_of_speech', 'jlpt_level', 'example']


class LibraryCache:
    def __init__(self, cards: list[WordConfig] = None):
        self.cards = cards or []

    def save(self):
        self.cards.sort(key=lambda x: (x.japanese[0].reading or x.japanese[0].word))
        with open(CACHE_DIR / LIBRARY_FILENAME, 'w') as file:
            file.write(jsonpickle.encode(self, warn=True))


def get_library() -> LibraryCache:
    """Load config object. Generates default configuration if no config file exists."""
    path = CACHE_DIR / LIBRARY_FILENAME

    # If there is no config file, generate a default config object
    if not os.path.isfile(path):
        return LibraryCache()
    # Otherwise load from file
    with open(path, 'r') as file:
        return jsonpickle.decode(file.read())


class HeaderConfig:
    def __init__(self, columns=None, deck: str = None, tags: list[str] = None, separator: str = 'comma'):
        self.columns = columns or VALID_FIELDS
        self.deck = deck
        self.tags = tags
        self.separator = separator


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
