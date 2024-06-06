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
@click.argument('text', nargs=-1)
@click.option('-ow', '--overwrite/--no-overwrite', is_flag=True, default=False,
              help='Overwrite cache contents if they already exist')
@click.option('-ss', '--senses', default=1, show_default=True,
              help='Number of sense definitions to include on the card (<=0 means all listed)')
def token(text, overwrite, senses):
    """
    Create a card from the jisho.org entry for each of the specified cached tokens.
    """
    text = reduce(lambda a, b: a.__str__() + " " + b.__str__(), text)
    token_request = Tokens.request(text).data
    if token_request is None:
        click.echo('No tokens found.')
        return
    click.echo('Found tokens:')
    click.echo(reduce(lambda a, b: a + '  ' + b, [f'({token_request.index(tk)}) {tk.token}' for tk in token_request]))

    prompted_indices = (click.prompt('Please enter a list of indices for the tokens you want to generate cards for',
                                     default='', show_default=False).split())
    indices = []
    for i in prompted_indices:
        try:
            indices.append(int(i))
        except ValueError:
            click.echo(f'Invalid index: {i}')
            return
    selected = [token_request[index].token for index in indices] if indices else [tk.token for tk in token_request]
    # generate word cards
    gen_words(selected, overwrite, senses)


@click.group("library")
def library():
    return


@library.command()
def view():
    """View the current cached 'library' of cards."""
    result = read_csv(CACHE_DIR / CACHE_FILENAME)
    click.echo(result if result else 'No cached cards.')


@library.command('export')
@click.option('-o', '--output-file', type=click.File('w'), default=DEFAULT_OUTFILE)
@click.option('-c', '--clear', is_flag=True, default=False, help='Clear cache after export')
def export(output_file, clear):
    """Export the current cached library to a CSV file."""
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
    update_settings({'tags': all_tags if all_tags else None})
    click.echo('Updated tags.')


@config.command()
@click.argument('deck', required=False, nargs=-1)
def deck(deck):
    update_settings({'deck': ' '.join(deck) if deck else None})
    click.echo('Updated deck.')


@config.command()
@click.argument('fields', nargs=-1)
@click.option('-v', '--valid-options', is_flag=True, default=False, )
def fields(fields, valid_options):
    # Supply list of valid options
    if valid_options:
        click.echo(f'Valid field options: {formatting.VALID_FIELDS}')
        return

    # If no fields, clear item
    if not fields:
        update_settings({'columns': None})
        return

    # Need at least two fields
    if fields.__len__() < 2:
        click.echo('No fields specified.')
        return

    # Check each provided field is valid
    for field in fields:
        if field not in formatting.VALID_FIELDS:
            click.echo(f'Couldn\'t update config, field {field} is invalid.')
            return

    # Make update
    update_settings({'columns': fields})
    click.echo('Updated fields.')
