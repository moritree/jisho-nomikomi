import os
from functools import reduce

from jisho_api.tokenize import Tokens
from jisho_api.word import Word

import formatting
from config import update_settings, read_config, CACHE_DIR, CACHE_FILENAME, TOKEN_CACHE_FILENAME
from output import (write_rows, cache_tokens, DEFAULT_OUTFILE,
                    write_export)
import click

from reading import read_csv


def gen_words(words: list[str], overwrite, senses):
    # generate csv rows for each word
    rows: list[list[str]] = []
    for w in words:
        wr = Word.request(w)
        if wr.data[0].japanese[0].word:
            click.echo(f'Found: {wr.data[0].japanese[0].word}（{wr.data[0].japanese[0].reading}）')
        else:
            click.echo(f'Found: {wr.data[0].japanese[0].reading}')
        rows.append(formatting.word_formatted(wr, formatting.VALID_FIELDS, senses))

    click.echo(f'Writing {rows.__len__()} words to cache...')
    failed = write_rows(CACHE_DIR / CACHE_FILENAME, rows, overwrite)
    if failed:
        print(f'Failed to write row(s) {reduce(lambda a, b: a.__str__() + ", " + b.__str__(),
                                               [rows.index(line) for line in failed])} (duplicate).')
    click.echo('Done.')


@click.command('word')
@click.argument('words', nargs=-1)
@click.option('-ow', '--overwrite/--no-overwrite', is_flag=True, default=False,
              help='Overwrite cache contents if they already exist')
@click.option('-ss', '--senses', default=1, show_default=True,
              help='Number of sense definitions to include on the card (<=0 means all listed)')
def word(words, overwrite, senses):
    """
    Create a card from the jisho.org entry on each of WORDS - this can be in English or Japanese (kanji, kana, romaji)
    """
    gen_words(words, overwrite, senses)


@click.command()
@click.argument('indices', nargs=-1, type=int)
@click.option('-ow', '--overwrite/--no-overwrite', is_flag=True, default=False,
              help='Overwrite cache contents if they already exist')
@click.option('-ss', '--senses', default=1, show_default=True,
              help='Number of sense definitions to include on the card (<=0 means all listed)')
def token(indices, overwrite, senses):
    """
    Create a card from the jisho.org entry for each of the specified cached tokens.
    """
    tokens = read_csv(CACHE_DIR / TOKEN_CACHE_FILENAME)[0]
    selected = [tokens[index] for index in indices] if indices else tokens
    # generate word cards
    gen_words(selected, overwrite, senses)


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
    indexed_string = cache_tokens([tk.token for tk in token_request.data])
    click.echo(indexed_string)


@click.command()
def library():
    """View the current cached 'library' of cards"""
    result = read_csv(CACHE_DIR / CACHE_FILENAME)
    click.echo(result if result else 'No cached cards.')


@click.command('export-cards')
@click.option('-o', '--output-file', type=click.File('w'), default=DEFAULT_OUTFILE)
@click.option('-c', '--clear', is_flag=True, default=False, help='Clear cache after export')
def export(output_file, clear):
    """Export the current cached 'library' of cards to a CSV file."""
    # Can't export from a nonexistent cache
    if not os.path.isfile(CACHE_DIR / CACHE_FILENAME):
        click.echo('No cached cards to export.')
        return

    # Export to csv file
    click.echo(f'Exporting cached cards to {output_file.name}...')
    write_export(output_file, read_csv(CACHE_DIR / CACHE_FILENAME))
    click.echo('Done.')

    # Clear cache
    if clear:
        click.echo(f'Clearing cache...')
        os.remove(CACHE_DIR / CACHE_FILENAME)
        click.echo('Done.')


@click.group("config")
@click.pass_context
def config(ctx):
    return


@config.command()
def view():
    """View the current config options."""
    click.echo(read_config())


@config.command()
@click.argument('all-tags', nargs=-1)
def tags(all_tags):
    update_settings({'tags': all_tags})
    click.echo('Updated tags.')


@config.command()
@click.argument('deck', nargs=1)
def deck(deck):
    update_settings({'deck': deck})
    click.echo('Updated deck.')


@config.command()
@click.argument('fields', nargs=-1)
@click.option('-v', '--valid-options', is_flag=True, default=False,)
def fields(fields, valid_options):
    if valid_options:
        click.echo(f'Valid field options: {formatting.VALID_FIELDS}')
        return
    update_settings({'columns': fields})
    click.echo('Updated fields.')
