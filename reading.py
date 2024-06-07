import csv
import os

from config import CSV_DIALECT


def read_csv(filename: str) -> list[list[str]]:
    """Returns contents of .csv file."""
    # don't even try if there's no file
    if not os.path.isfile(filename):
        return []
    with open(filename, 'r') as file:
        return list(csv.reader(file, dialect=CSV_DIALECT))


def line_exists(filename: str, line: str) -> bool:
    """Returns whether the given line already exists in the given file."""
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
