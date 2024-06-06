import os
from functools import reduce

from jisho_api.tokenize import Tokens
from jisho_api.word import Word

import formatting
from config import update_settings, read_config, CACHE_DIR, CACHE_FILENAME, TOKEN_CACHE_FILENAME, get_config_value, \
    CONFIG_FILENAME
from output import (write_rows, cache_tokens, DEFAULT_OUTFILE,
                    write_export)
import click

from reading import read_csv


def gen_words(words: list[str], overwrite: bool, senses):
    """Get and cache info on each word in the provided list of words."""
    # generate csv rows for each word
    rows: list[list[str]] = []
    conf_cols = get_config_value('columns')
    card_fields = conf_cols if conf_cols is not None else formatting.VALID_FIELDS
    for w in words:
        wr = Word.request(w)
        if wr.data[0].japanese[0].word:
            click.echo(f'Found: {wr.data[0].japanese[0].word}（{wr.data[0].japanese[0].reading}）')
        else:
            click.echo(f'Found: {wr.data[0].japanese[0].reading}')
        rows.append(formatting.word_formatted(wr, card_fields, senses))

    # write rows
    click.echo(f'Writing {rows.__len__()} words to cache...')
    failed = write_rows(CACHE_DIR / CACHE_FILENAME, rows, overwrite)
    if failed:
        click.echo(f'Failed to write row(s) {reduce(lambda a, b: a.__str__() + ", " + b.__str__(),
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
    Create a card from the jisho.org entry on each of WORDS.
    This can be in English or Japanese (kanji, kana, romaji).
    """
    gen_words(words, overwrite, senses)


@click.command()
@click.argument('text', nargs=-1)
@click.option('-ow', '--overwrite/--no-overwrite', is_flag=True, default=False,
              help='Overwrite cache contents if they already exist')
@click.option('-ss', '--senses', default=1, show_default=True,
              help='Number of sense definitions to include on the card (<=0 means all listed)')
@click.option('-all', is_flag=True, default=False,
              help='Cache every found token without asking user to select indices')
def token(text, overwrite, senses, all):
    """
    Split the provided text into Japanese tokens, and write user selected set of them to cache.
    """
    text = reduce(lambda a, b: a.__str__() + " " + b.__str__(), text)
    token_request = Tokens.request(text)

    # abort if there are no matching tokens
    if token_request is None:
        click.echo('No tokens found.')
        return

    click.echo('Found tokens:')
    data = token_request.data
    click.echo('  '.join([f'({data.index(tk)}) {tk.token}' for tk in data]))

    # get indices
    prompted_indices = (click.prompt('Please enter a list of indices for the tokens you want to generate cards for',
                                     default='', show_default=False).split()) if not all else []
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
    """View information on the current cached library of words to be translated into cards."""
    result = read_csv(CACHE_DIR / CACHE_FILENAME)
    click.echo(result if result else 'No cached cards.')


@library.command()
def clear():
    """Clear library cache."""
    if os.path.isfile(CACHE_DIR / CACHE_FILENAME):
        if click.confirm('Are you sure you want to clear cache?', abort=True):
            os.remove(CACHE_DIR / CACHE_FILENAME)
            click.echo('Cache cleared.')
    else:
        click.echo('No cache to clear.')


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
    """Update the tags list in the config file, for tags that will be automatically applied to each card on import.
    If no tags are specified, the field is removed."""
    update_settings({'tags': all_tags if all_tags else None})
    click.echo('Updated tags.')


@config.command()
@click.argument('deck', required=False, nargs=-1)
def deck(deck):
    """Update the deck name in the config file. If no name is specified, the field is removed."""
    update_settings({'deck': ' '.join(deck) if deck else None})
    click.echo('Updated deck.')


@config.command()
@click.argument('fields', nargs=-1)
@click.option('-v', '--valid-options', is_flag=True, default=False, )
def fields(fields, valid_options):
    """Update the fields list in the config file. If no values are specified, the field is removed."""
    # supply list of valid options
    if valid_options:
        click.echo(f'Valid field options: {formatting.VALID_FIELDS}')
        return

    # if no fields, clear item
    if not fields:
        update_settings({'columns': None})
        return

    # need at least two fields
    if fields.__len__() < 2:
        click.echo('No fields specified.')
        return

    # check each provided field is valid
    for field in fields:
        if field not in formatting.VALID_FIELDS:
            click.echo(f'Couldn\'t update config, field {field} is invalid.')
            return

    original_vocab_field = get_config_value('columns').index('vocab') or formatting.VALID_FIELDS.index('vocab')

    # make config update
    update_settings({'columns': fields})
    click.echo('Updated fields.')

    # regenerate all cards if fields are changed
    click.echo('Regenerating cards to match new field configuration')
    lines = [line[original_vocab_field] for line in read_csv(CACHE_DIR / CACHE_FILENAME)]
    gen_words(lines, True, 1)


@config.command()
def clear():
    """Clear config file."""
    if os.path.isfile(CACHE_DIR / CONFIG_FILENAME):
        if click.confirm('Are you sure you want to clear config file?', abort=True):
            os.remove(CACHE_DIR / CONFIG_FILENAME)
            click.echo('Config file cleared.')
    else:
        click.echo('No config file to clear.')
