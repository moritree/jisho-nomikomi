from jisho_api.word import Word

import formatting
from output import write_csv
import click


@click.command()
@click.option('--jap')
def word_file(jap):
    w = Word.request(jap)
    print('writing to csv: ' + w.data[0].japanese[0].word)
    write_csv('out.csv', formatting.word_formatted(w, formatting.VALID_FIELDS))
