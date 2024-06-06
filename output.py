import csv
from functools import reduce

from config import CACHE_DIR, TOKEN_CACHE_FILENAME
from formatting import CSV_DIALECT, csv_header, csv_formatted_item
from reading import line_exists

DEFAULT_OUTFILE = 'out.csv'


def cache_tokens(tokens: list[str]) -> str:
    """Caches the tokens so they can be used later."""
    max_token_length = reduce(lambda a, b: a if a > b else b, [token.__len__() for token in tokens])
    associated_index = ((tokens.index(token), token) for token in tokens)

    CACHE_DIR.mkdir(exist_ok=True)
    with open(CACHE_DIR / TOKEN_CACHE_FILENAME, 'w') as cache_file:
        writer = csv.writer(cache_file, dialect=CSV_DIALECT)
        writer.writerow(tokens)
        return reduce(lambda a, b : a + '  ' + b, [f'({tokens.index(token)}) {token}' for token in tokens])


def write_export(file, lines: list[list[str]]):
    """Exports the cached cards into an anki formatted file."""
    # write header
    file.write(csv_header())
    for line in lines:
        file.write(csv_formatted_item(line))


def write_rows(filename: str, lines: list[list[str]], overwrite: bool = False) -> list[list[str]]:
    """
    Writes each item to a file in .csv format.
    :returns: The list of any items which could not be written.
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
