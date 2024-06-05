from jisho_api.word import Word

import formatting
from output import write_item_to_csv
import click


@click.command("word")
@click.argument('words', nargs=-1)
@click.option('-o', '--output-filename', default='out.csv', show_default=True)
@click.option('-ow', '--overwrite/--no-overwrite', is_flag=True, default=False,
              help="Overwrite the contents of any existing output file")
@click.option('-ss', '--senses', default=1, show_default=True,
              help="Number of sense definitions to include on the card (<=0 means all listed)")
def cards_from_words(words, output_filename, overwrite, senses):
    """
    Create a card from the jisho.org entry on each of WORDS - this can be in English or Japanese (kanji, kana, romaji)
    """
    for w in words:
        wr = Word.request(w)
        if wr.data[0].japanese[0].word:
            click.echo(f'Found: {wr.data[0].japanese[0].word} ({wr.data[0].japanese[0].reading})')
        else:
            click.echo(f'Found: {wr.data[0].japanese[0].reading}')
        click.echo(f'Writing...')
        try:
            write_item_to_csv(output_filename, formatting.word_formatted(wr, formatting.VALID_FIELDS, senses), overwrite)
        except RuntimeError as e:
            print("Failed to write: " + e.__str__())
        click.echo('Done.')

        # don't overwrite every SINGLE word as we go, that would be silly
        if overwrite:
            overwrite = False
