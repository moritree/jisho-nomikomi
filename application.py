from jisho_api.word import Word

import formatting
from output import write_item_to_csv
import click


@click.command()
@click.option('-j', '--japanese')
@click.option('-o', '--output-filename', default='out.csv', show_default=True)
@click.option('-ow', '--overwrite', is_flag=True, default=False, help="Overwrite an existing output file")
def word_file(japanese, output_filename, overwrite):
    w = Word.request(japanese)
    print('writing to csv: ' + w.data[0].japanese[0].word)
    try:
        write_item_to_csv(output_filename, formatting.word_formatted(w, formatting.VALID_FIELDS), overwrite)
    except RuntimeError as e:
        print("Failed to write: " + e.__str__())
