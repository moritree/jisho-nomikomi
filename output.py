import csv
from functools import reduce
from pathlib import Path

import jsonpickle
from jisho_api.word.cfg import WordConfig

from configuration import CACHE_DIR, TOKEN_CACHE_FILENAME, load_json, CSV_DIALECT, LIBRARY_FILENAME
from formatting import csv_header, word_to_csv
from reading import line_exists

DEFAULT_OUTFILE = 'out.csv'


def export_to_csv(src: Path=CACHE_DIR / LIBRARY_FILENAME, out=DEFAULT_OUTFILE):
    """Export cached data to CSV file."""
    data = {}
    with open(src, 'r') as file:
        data = jsonpickle.decode(file.read())

    out.write(csv_header())
    for row in [word_to_csv(jsonpickle.decode(v)) for k, v in data.items()]:
        out.write(row)
