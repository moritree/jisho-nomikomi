import os
from functools import reduce

from jisho_api.tokenize import Tokens
from jisho_api.word import Word

import formatting
from config import update_json, load_json, CACHE_DIR, CACHE_FILENAME, CONFIG_FILENAME
from output import write_rows, DEFAULT_OUTFILE, write_export
import click

from reading import read_csv


def gen_words(words: list[str], overwrite: bool, senses):
    """Get and cache info on each word in the provided list of words."""
    # generate csv rows for each word
    rows: list[list[str]] = []
    card_fields = load_json(CACHE_DIR / CONFIG_FILENAME).get('columns') or formatting.VALID_FIELDS

    data_chunks = [wr.data[0] for wr in filter(lambda x: x is not None, [Word.request(w) for w in words])]
    click.echo(f'Found {', '.join(w.japanese[0].word for w in data_chunks)}')
    #
    # for w in words:
    #     wr = Word.request(w)
    #     if wr.data[0].japanese[0].word:
    #         click.echo(f'Found: {wr.data[0].japanese[0].word}（{wr.data[0].japanese[0].reading}）')
    #     else:
    #         click.echo(f'Found: {wr.data[0].japanese[0].reading}')
    #     rows.append(formatting.word_formatted(wr, card_fields, senses))

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
@click.option('-ss', '--senses', default=1, show_default=True,
              help='Number of sense definitions to include on the card (less than 1 means all listed).')
@click.option('-ow', '--overwrite/--no-overwrite', is_flag=True, default=False,
              help='Overwrite cache contents if they already exist.')
@click.option('-all', 'all_tokens', is_flag=True, default=False,
              help='Cache every found token without first asking user to specify indices.')
def token(text, senses, overwrite, all_tokens):
    """
    Split the provided text into Japanese tokens, and write user determined set of these to cache.
    """
    if not text:
        click.echo('No text provided.')
        return

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
                                     default='', show_default=False).split()) if not all_tokens else []
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
@click.option('-c', '--clear', 'clear_after_export', is_flag=True, default=False, help='Clear cache after export')
def export(output_file, clear_after_export):
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
    if clear_after_export:
        click.echo(f'Clearing cache...')
        os.remove(CACHE_DIR / CACHE_FILENAME)
        click.echo('Done.')


@click.group('config')
@click.pass_context
def config(ctx):
    return


@config.command()
def view():
    """View the current config options."""
    click.echo(load_json(CACHE_DIR / CONFIG_FILENAME) or 'No config file to view.')


@config.command()
def clear_after():
    """Clear config file."""
    if os.path.isfile(CACHE_DIR / CONFIG_FILENAME):
        if click.confirm('Are you sure you want to clear config file?', abort=True):
            os.remove(CACHE_DIR / CONFIG_FILENAME)
            click.echo('Config file cleared.')
    else:
        click.echo('No config file to clear.')


@click.group('header')
@click.pass_context
def header(ctx):
    """Configure items for Anki file header."""
    return


@header.command()
@click.argument('all-tags', nargs=-1)
@click.option('-rm', '--remove', is_flag=True, default=False, help='Remove field from header')
def tags(all_tags, remove):
    """Update the tags list. For tags that will be automatically applied to each card on import."""
    if remove:
        update_json({'tags': None}, CACHE_DIR / CONFIG_FILENAME)
        click.echo('Removed tags field.')
    elif all_tags:
        update_json({'tags': all_tags}, CACHE_DIR / CONFIG_FILENAME)
        click.echo('Updated tags.')
    else:
        click.echo('No tags to update. Include at least one tag argument.')


@header.command()
@click.argument('title', required=False, nargs=-1)
@click.option('-rm', '--remove', is_flag=True, default=False, help='Remove field from header')
def deck(title, remove):
    """Update the deck title."""
    if remove:
        update_json({'deck': None}, CACHE_DIR / CONFIG_FILENAME)
        click.echo('Removed deck field.')
    elif title:
        update_json({'deck': ' '.join(title)}, CACHE_DIR / CONFIG_FILENAME)
        click.echo('Updated deck.')
    else:
        click.echo('No deck to update. Include at least one deck argument.')


@header.command()
@click.argument('order_format', nargs=-1)
@click.option('-v', '--valid-options', is_flag=True, default=False)
@click.option('-rm', '--remove', is_flag=True, default=False, help='Remove field from header')
def columns(order_format, valid_options, remove):
    """Update the fields list. If no values are specified, the field is removed."""
    # supply list of valid options
    if valid_options:
        click.echo(f'Valid field options: {formatting.VALID_FIELDS}')
        return

    if remove:
        update_json({'columns': None}, CACHE_DIR / CONFIG_FILENAME)
        click.echo('Removed fields field.')
    elif not order_format:
        # if no fields, clear item
        click.echo('No columns to update. Include at least one column argument.')
    elif order_format.__len__() < 2:
        # need at least two fields
        click.echo('No fields specified.')
    else:
        # try to write fields
        # check each provided field is valid
        for field in order_format:
            if field not in formatting.VALID_FIELDS:
                click.echo(f'Couldn\'t update config, field {field} is invalid.')
                return

        # index in cache of vocab field
        cols: list = load_json(CACHE_DIR / CONFIG_FILENAME).get('columns')
        original_vocab_field = cols.index('vocab') if cols and cols.__contains__('vocab') \
            else formatting.VALID_FIELDS.index('vocab')

        # make config update
        update_json({'columns': order_format}, CACHE_DIR / CONFIG_FILENAME)
        click.echo('Updated fields.')


config.add_command(header)
