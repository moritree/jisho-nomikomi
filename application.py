from functools import reduce

from jisho_api.tokenize import Tokens
from jisho_api.word import Word

import formatting
from output import write_rows, cache_tokens, CACHE_PATH, DEFAULT_OUTFILE
import click

from reading import read_csv


def gen_words(words: list[str], output_filename, overwrite, senses):
    # generate csv rows for each word
    rows: list[list[str]] = []
    for w in words:
        wr = Word.request(w)
        if wr.data[0].japanese[0].word:
            click.echo(f'Found: {wr.data[0].japanese[0].word}（{wr.data[0].japanese[0].reading}）')
        else:
            click.echo(f'Found: {wr.data[0].japanese[0].reading}')
        rows.append(formatting.word_formatted(wr, formatting.VALID_FIELDS, senses))

    click.echo(f'Writing {rows.__len__()} words to {output_filename}...')
    failed = write_rows(output_filename, rows, overwrite)
    if failed:
        print(f'Failed to write row(s) {reduce(lambda a, b: a.__str__() + ", " + b.__str__(),
                                               [rows.index(line) for line in failed])}.')
    click.echo('Done.')


@click.command("word")
@click.argument('words', nargs=-1)
@click.option('-o', '--output-filename', default=DEFAULT_OUTFILE, show_default=True)
@click.option('-ow', '--overwrite/--no-overwrite', is_flag=True, default=False,
              help="Overwrite the contents of any existing output file")
@click.option('-ss', '--senses', default=1, show_default=True,
              help="Number of sense definitions to include on the card (<=0 means all listed)")
def word(words, output_filename, overwrite, senses):
    """
    Create a card from the jisho.org entry on each of WORDS - this can be in English or Japanese (kanji, kana, romaji)
    """
    gen_words(words, output_filename, overwrite, senses)


@click.command()
@click.argument('indices', nargs=-1, type=int)
@click.option('-o', '--output-filename', default=DEFAULT_OUTFILE, show_default=True)
@click.option('-ow', '--overwrite/--no-overwrite', is_flag=True, default=False,
              help="Overwrite the contents of any existing output file")
@click.option('-ss', '--senses', default=1, show_default=True,
              help="Number of sense definitions to include on the card (<=0 means all listed)")
def token(indices, output_filename, overwrite, senses):
    """
    Create a card from the jisho.org entry for each of the specified cached tokens.
    """
    tokens = read_csv(CACHE_PATH)[0]
    selected = [tokens[index] for index in indices] if indices else tokens
    # generate word cards
    gen_words(selected, output_filename, overwrite, senses)


@click.command()
@click.argument('text', nargs=-1)
def tokenise(text):
    """
    Collect and cache tokens from the given Japanese text.
    After running this command you may want to run `token [INDICES]` to generate cards from these tokens.
    """
    token_request = Tokens.request(reduce(lambda a, b: a.__str__() + " " + b.__str__(), text))
    if token_request is None:
        click.echo('No tokens found.')
        return
    indexed_string = cache_tokens([token.token for token in token_request.data])
    click.echo(indexed_string)
