import csv


def csv_header(tags: str, deck: str) -> str:  # Anki header data
    return ''.join([
        'separator:comma',
        f'\ndeck:{deck}' if deck else '',
        f'\ntags:{tags}' if tags else ''
    ])


def write_csv(filename: str, rows: list[str]):
    with (open(filename, 'w', newline='')) as csvfile:
        writer = csv.writer(csvfile, dialect='unix')
        writer.writerow(rows)
