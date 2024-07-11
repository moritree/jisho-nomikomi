import os
from typing import Self

import jsonpickle
from pathlib import Path

from jisho_api.sentence.cfg import SentenceConfig
from jisho_api.word.cfg import WordConfig

CACHE_DIR: Path = Path.home() / '.nomikomi'


class Examples:
    PATH = CACHE_DIR / 'examples.json'

    def __init__(self, examples: dict[str, SentenceConfig] = None):
        self.examples = examples or {}

    def save(self):
        path = Examples.PATH
        if self.examples:
            with open(path, 'w') as file:
                file.write(jsonpickle.encode(self, warn=True))
        elif os.path.isfile(path):
            os.remove(path)

    @staticmethod
    def delete_file():
        if os.path.isfile(Examples.PATH):
            os.remove(Examples.PATH)

    @classmethod
    def get(cls) -> Self:
        """Load config object. Generates default configuration if no config file exists."""
        # If there is no config file, generate a config object with default values
        if not os.path.isfile(cls.PATH):
            return cls()
        # Otherwise load from file
        with open(cls.PATH, 'r') as file:
            return jsonpickle.decode(file.read())


class Library:
    PATH = CACHE_DIR / 'library.json'

    def __init__(self, cards: list[WordConfig] = None):
        self.cards = cards or []

    def save(self):
        # sort cards
        self.cards.sort(key=lambda x: (x.japanese[0].reading or x.japanese[0].word))

        # remove duplicates (sorted so only need to check neighbors)
        # can't use turning into set/dict, because WordConfig type. this is fine
        to_remove: list[WordConfig] = []
        for i in range(self.cards.__len__() - 1):
            if self.cards[i] == self.cards[i + 1]:
                to_remove.append(self.cards[i])
        for c in to_remove:
            self.cards.remove(c)

        if self.cards:
            with open(Library.PATH, 'w') as file:
                file.write(jsonpickle.encode(self, warn=True))
        # if there are no cards, don't bother writing an empty file, delete anything that's there
        elif os.path.isfile(Library.PATH):
            os.remove(Library.PATH)

    @staticmethod
    def delete_file():
        if os.path.isfile(Library.PATH):
            os.remove(Library.PATH)

    @classmethod
    def get(cls) -> Self:
        """Load library object. Generates empty object if no library file exists."""
        # If there is no config file, generate a default config object
        if not os.path.isfile(cls.PATH):
            return cls()
        # Otherwise load from file
        with open(cls.PATH, 'r') as file:
            return jsonpickle.decode(file.read())


class Config:
    PATH = CACHE_DIR / 'config.json'

    class _HeaderConfig:
        VALID_FIELDS = ['vocab', 'kana', 'translation', 'part_of_speech', 'jlpt_level', 'example']

        def __init__(self, columns=None, deck: str = None, tags: list[str] = None, separator: str = 'comma'):
            self.separator = separator
            self.columns = columns or self.VALID_FIELDS
            self.deck = deck
            self.tags = tags

        def update_columns(self, columns: list[str]):
            for col in columns:
                if col not in self.VALID_FIELDS:
                    raise KeyError(f'Field "{col}" is not valid')
            self.columns = columns

    VALID_HEADER_FIELDS = _HeaderConfig.VALID_FIELDS

    def __init__(self, header: _HeaderConfig = _HeaderConfig(), senses: int = 1):
        self.header = header
        self.senses = senses

    def save(self):
        with open(Config.PATH, 'w') as file:
            file.write(jsonpickle.encode(self))

    def __str__(self):
        return f'header: {self.header.__dict__},\nsenses: {self.senses}'

    @staticmethod
    def delete_file():
        if os.path.isfile(Config.PATH):
            os.remove(Config.PATH)

    @classmethod
    def get(cls) -> Self:
        """Load config object. Generates default configuration if no config file exists."""
        # If there is no config file, generate a default config object
        if not os.path.isfile(Config.PATH):
            return cls()

        # Otherwise load from file
        with open(cls.PATH, 'r') as file:
            return jsonpickle.decode(file.read())
