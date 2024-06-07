import jsonpickle
import configuration
from formatting import csv_header, word_to_csv, CSV_DIALECT

DEFAULT_OUTFILE = 'out.csv'


def export_to_csv(src, out):
    """Export cached data to CSV file."""
    config = configuration.get_config()

    data = {}
    with open(src, 'r') as file:
        data = jsonpickle.decode(file.read())

    out.write(csv_header(config))
    for row in [word_to_csv(jsonpickle.decode(v), config) for k, v in data.items()]:
        out.write(row)
