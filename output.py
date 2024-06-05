import csv
import io
import os


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


def write_rows(filename: str, lines: list[list[str]], overwrite: bool = False) -> list[list[str]]:
    """
    Write each item to a csv file.
    :param filename:
    :param lines:
    :param overwrite:
    :return: Any lines that were not able to be written
    """
    already_exists = os.path.isfile(filename)
    failed: list[list[str]] = []
    with (open(filename, 'w' if overwrite else 'a', newline='')) as file:
        # write Anki header if necessary
        if not already_exists or overwrite:
            file.write(csv_header())
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
