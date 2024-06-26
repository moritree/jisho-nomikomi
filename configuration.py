import os
import jsonpickle
from pathlib import Path

from jisho_api.sentence.cfg import SentenceConfig
from jisho_api.word.cfg import WordConfig

CONFIG_FILENAME = 'config.json'
LIBRARY_FILENAME = 'library.json'
EXAMPLES_FILENAME = 'examples.json'
CACHE_DIR: Path = Path.home() / '.nomikomi'
TOKEN_CACHE_FILENAME = 'token_cache.csv'
VALID_FIELDS = ['vocab', 'kana', 'translation', 'part_of_speech', 'jlpt_level', 'example']


class ExamplesCache:
    def __init__(self, examples: dict[str, SentenceConfig] = None):
        self.examples = examples or {}

    def save(self):
        # remove duplicates (sorted so only need to check neighbors
        # can't use turning into set/dict, because WordConfig type. this is fine
        with open(CACHE_DIR / EXAMPLES_FILENAME, 'w') as file:
            file.write(jsonpickle.encode(self, warn=True))


def get_examples() -> ExamplesCache:
    """Load config object. Generates default configuration if no config file exists."""
    path = CACHE_DIR / EXAMPLES_FILENAME

    # If there is no config file, generate a default config object
    if not os.path.isfile(path):
        return ExamplesCache()
    # Otherwise load from file
    with open(path, 'r') as file:
        return jsonpickle.decode(file.read())


class LibraryCache:
    def __init__(self, cards: list[WordConfig] = None):
        self.cards = cards or []

    def save(self):
        # sort cards
        self.cards.sort(key=lambda x: (x.japanese[0].reading or x.japanese[0].word))

        # remove duplicates (sorted so only need to check neighbors
        # can't use turning into set/dict, because WordConfig type. this is fine
        to_remove: list[WordConfig] = []
        for i in range(self.cards.__len__() - 1):
            if self.cards[i] == self.cards[i + 1]:
                to_remove.append(self.cards[i])
        for c in to_remove:
            self.cards.remove(c)

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
        self.separator = separator
        self.columns = columns or VALID_FIELDS
        self.deck = deck
        self.tags = tags


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
