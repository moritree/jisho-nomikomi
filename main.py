from jisho_api.word import Word

import formatting
from output import write_csv

if __name__ == '__main__':
    r = Word.request('人')
    write_csv("test.csv", formatting.word_formatted(r, formatting.VALID_FIELDS))
