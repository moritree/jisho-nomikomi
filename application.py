from jisho_api.word import Word

import formatting
from output import write_item_to_csv
import click


@click.command()
@click.option('-j', '--japanese', help="Japanese word (kanji, kana, romaji)")
@click.option('-o', '--output-filename', default='out.csv', show_default=True)
@click.option('-ow', '--overwrite/--no-overwrite', is_flag=True, default=False,
              help="Overwrite the contents of any existing output file")
@click.option('-ss', '--senses', default=1, show_default=True,
              help="Number of sense definitions to include on the card (<=0 for all)")
def word_card(japanese, output_filename, overwrite, senses):
    w = Word.request(japanese)
    click.echo(f'Writing card row for {japanese}')
    try:
        write_item_to_csv(output_filename, formatting.word_formatted(w, formatting.VALID_FIELDS, senses), overwrite)
    except RuntimeError as e:
        print("Failed to write: " + e.__str__())
