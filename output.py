import csv
from functools import reduce
from pathlib import Path

import jsonpickle
from jisho_api.word.cfg import WordConfig

from config import CACHE_DIR, TOKEN_CACHE_FILENAME, load_json, CSV_DIALECT
from formatting import csv_header, csv_formatted_item, csv_row_from_json
from reading import line_exists

DEFAULT_OUTFILE = 'out.csv'


def export_to_csv(src: Path, out):
    data = {}
    with open (src, 'r') as file:
        data = jsonpickle.decode(file.read())

    out.write(csv_header())
    for row in [csv_row_from_json(jsonpickle.decode(v)) for k, v in data.items()]:
        out.write(row)
