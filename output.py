import csv
import io
import os


def csv_header(tags: str = None, deck: str = None) -> str:  # Anki header data
    return ''.join([
        '#separator:comma',
        f'\n#deck:{deck}' if deck else '',
        f'\n#tags:{tags}' if tags else '',
        '\n'
    ])


def csv_formatted_item(item: list[str]) -> str:
    out = io.StringIO()
    writer = csv.writer(out, dialect='unix')
    writer.writerow(item)
    out.seek(0)
    return out.read()


def write_item_to_csv(filename: str, item: list[str], overwrite: bool = False):
    already_exists = os.path.isfile(filename)
    with (open(filename, 'w' if overwrite else 'a', newline='')) as csvfile:
        # don't need to write anything if this item already exists in the file
        if line_exists(filename, csv_formatted_item(item)):
            raise RuntimeError('Line for this word already exists')
        # write Anki header if necessary
        if not already_exists or overwrite:
            csvfile.write(csv_header())
        # write row in csv format
        csvfile.write(csv_formatted_item(item))


def line_exists(filename: str, line: str) -> bool:
    # if there's no file, this line is definitely not in it
    if not os.path.isfile(filename):
        return False
    # read & check whether this line is in the file already
    # TODO make more efficient - maybe write in alphabetical order, binary search?
    with open(filename, 'r') as file:
        lines = file.readlines()
        if lines.__contains__(line):
            return True
    return False
