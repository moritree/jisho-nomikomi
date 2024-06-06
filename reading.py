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
