import jisho_api

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from jisho_api.word import Word
from jisho_api.word.request import WordRequest

import formatting
from output import write_csv

if __name__ == '__main__':
    r = Word.request('人')
    write_csv("test.csv", formatting.word_formatted(r, formatting.VALID_FIELDS))
    # print(r)
