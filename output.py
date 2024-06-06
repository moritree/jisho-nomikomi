import csv
from functools import reduce

from config import CACHE_DIR, TOKEN_CACHE_FILENAME
from formatting import CSV_DIALECT, csv_header, csv_formatted_item
from reading import line_exists

DEFAULT_OUTFILE = 'out.csv'


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
