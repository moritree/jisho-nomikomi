import csv
import os


def csv_header(tags: str = None, deck: str = None) -> str:  # Anki header data
    return ''.join([
        'separator:comma',
        f'\ndeck:{deck}' if deck else '',
        f'\ntags:{tags}' if tags else '',
        '\n'
    ])


def write_csv(filename: str, rows: list[str], overwrite: bool = False):
    already_exists = os.path.isfile(filename)
    with (open(filename, 'w' if overwrite else 'a', newline='')) as csvfile:
        if not already_exists or overwrite:
            csvfile.write(csv_header())

        writer = csv.writer(csvfile, dialect='unix')
        writer.writerow(rows)
