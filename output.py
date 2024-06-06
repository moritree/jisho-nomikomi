import csv
import io
import os
import shutil
from functools import reduce
from pathlib import Path

from formatting import CSV_DIALECT, csv_header
from reading import line_exists

CACHE_DIR: Path = Path.home() / '.nomikomi'
CACHE_FILENAME = 'cache.csv'
TOKEN_CACHE_FILENAME = 'token_cache.csv'
DEFAULT_OUTFILE = 'out.csv'


def cache_tokens(tokens: list[str]) -> str:
    max_token_length = reduce(lambda a, b: a if a > b else b, [token.__len__() for token in tokens])
    associated_index = ((tokens.index(token), token) for token in tokens)

    CACHE_DIR.mkdir(exist_ok=True)
    with open(CACHE_DIR / TOKEN_CACHE_FILENAME, 'w') as cache_file:
        writer = csv.writer(cache_file, dialect=CSV_DIALECT)
        writer.writerow(tokens)
        return reduce(lambda a, b : a + '  ' + b, [f'({tokens.index(token)}) {token}' for token in tokens])


def csv_formatted_item(item: list[str]) -> str:
    out = io.StringIO()
    writer = csv.writer(out, dialect=CSV_DIALECT)
    writer.writerow(item)
    out.seek(0)
    return out.read()


def write_export(file, lines: list[list[str]], deck=None, tags=None):
    # write header
    file.write(csv_header(deck=deck, tags=tags))
    for line in lines:
        file.write(csv_formatted_item(line))


def write_rows(filename: str, lines: list[list[str]], overwrite: bool = False) -> list[list[str]]:
    """
    Write each item to a csv file.
    :param filename:
    :param lines:
    :param overwrite:
    :return: Any lines that were not able to be written
    """
    failed: list[list[str]] = []
    with (open(filename, 'w' if overwrite else 'a', newline='')) as file:
        # write each line
        for line in lines:
            formatted = csv_formatted_item(line)
            # don't need to write anything if this item already exists in the file
            if line_exists(filename, formatted):
                failed.append(line)
                continue
            # write row in csv format
            file.write(formatted)
    return failed
