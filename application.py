import os
from functools import reduce

import jsonpickle
from jisho_api.tokenize import Tokens
from jisho_api.word import Word

import configuration
from configuration import load_json, CACHE_DIR, CONFIG_FILENAME, LIBRARY_FILENAME
from formatting import word_to_csv, csv_header
import click


def gen_words(words: list[str]):
    """Get and cache info on each word in the provided list of words."""
    data_chunks = {wr.data[0].slug: jsonpickle.encode(wr.data[0]) for wr in
                   filter(lambda x: x is not None, [Word.request(w) for w in filter(lambda y: y is not None, words)])}
    click.echo(f'Found {', '.join(data_chunks.keys())}')

    # write rows
    click.echo(f'Writing {data_chunks.__len__()} words to cache...')
    configuration.update_json(data_chunks, CACHE_DIR / LIBRARY_FILENAME)
    click.echo('Done.')


@click.command('word')
@click.argument('words', nargs=-1)
def word(words):
    """
    Create a card from the jisho.org entry on each of WORDS.
    This can be in English or Japanese (kanji, kana, romaji).
    """
    gen_words(words)


@click.command()
@click.argument('text', nargs=-1)
@click.option('-all', 'all_tokens', is_flag=True, default=False,
              help='Cache every found token without first asking user to specify indices.')
def token(text, all_tokens):
    """
    Split the provided text into Japanese tokens, and write user determined set of these to cache.
    """
    if not text:
        click.echo('No text provided.')
        return

    text = ' '.join(text)
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
    selected = [data[index].token for index in indices] if indices else [tk.token for tk in data]

    # generate word cards
    gen_words(selected)


@click.group('library')
def library():
    return


@library.command()
def view():
    """View information on the current cached library of words."""
    result = load_json(CACHE_DIR / LIBRARY_FILENAME)
    click.echo(', '.join(result.keys()) if result else 'No cached cards.')


@library.command()
def clear():
    """Clear library cache."""
    if os.path.isfile(CACHE_DIR / LIBRARY_FILENAME):
        if click.confirm('Are you sure you want to clear library?', abort=True):
            os.remove(CACHE_DIR / LIBRARY_FILENAME)
            click.echo('Library cache cleared.')
    else:
        click.echo('No library cache to clear.')


@library.command('export')
@click.option('-o', '--output-file', type=click.File('w'), default='out.csv')
@click.option('-c', '--clear', 'clear_after_export', is_flag=True, default=False,
              help='Clear library cache after exporting.')
def export(output_file, clear_after_export):
    """Export the current cached library to a CSV file."""
    # can't export from a nonexistent library
    if not os.path.isfile(CACHE_DIR / LIBRARY_FILENAME):
        click.echo('No cached cards to export.')
        return
    configs = configuration.get_config()

    # gather card data
    data = {}
    with open(CACHE_DIR / LIBRARY_FILENAME, 'r') as file:
        data = jsonpickle.decode(file.read())

    # write export
    output_file.write(csv_header(configs))
    for row in [word_to_csv(jsonpickle.decode(v), configs) for k, v in data.items()]:
        output_file.write(row)

    # clear cache
    if clear_after_export:
        click.echo(f'Clearing library cache...')
        os.remove(CACHE_DIR / LIBRARY_FILENAME)
        click.echo('Done.')


@click.group('config')
@click.pass_context
def config(ctx):
    return


@config.command()
def view():
    """View the current config options."""
    click.echo(configuration.get_config().__str__() or 'No config file to view.')


@config.command()
def clear():
    """Clear config file."""
    if os.path.isfile(CACHE_DIR / CONFIG_FILENAME):
        if click.confirm('Are you sure you want to clear config file?', abort=True):
            os.remove(CACHE_DIR / CONFIG_FILENAME)
            click.echo('Config file cleared.')
    else:
        click.echo('No config file to clear.')


@config.command()
@click.argument('senses', nargs=1, type=int)
@click.option('-rm', '--remove', is_flag=True, default=False, help='')
def senses(senses, remove):
    """The (max) number of senses to export for each word."""
    configs = configuration.get_config()
    configs.senses = None if remove else senses
    configs.save()
    click.echo('Senses value updated.')


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
    configs = configuration.get_config()
    if remove:
        configs.header.tags = None
    elif all_tags:
        configs.header.tags = all_tags
    configs.save()
    click.echo('Header tags updated.')


@header.command()
@click.argument('title', required=False, nargs=-1)
@click.option('-rm', '--remove', is_flag=True, default=False, help='Remove field from header')
def deck(title, remove):
    """Update the deck title."""
    configs = configuration.get_config()
    if remove:
        configs.header.deck = None
    elif title:
        configs.header.deck = title
    configs.save()
    click.echo('Header deck updated.')


@header.command()
@click.argument('order_format', nargs=-1, required=True)
@click.option('-v', '--valid-options', is_flag=True, default=False)
@click.option('-rm', '--remove', is_flag=True, default=False, help='Remove field from header')
def columns(order_format, valid_options, remove):
    """Update the fields list. If no values are specified, the field is removed."""
    # supply list of valid options
    if valid_options:
        click.echo(f'Valid field options: {configuration.VALID_FIELDS}')
        return

    configs = configuration.get_config()
    if remove:
        configs.header.tags = None
        configs.save()
    elif order_format.__len__() < 2:
        # need at least two fields
        click.echo('No fields specified.')
    else:
        # try to write fields
        # check each provided field is valid
        for field in order_format:
            if field not in configuration.VALID_FIELDS:
                click.echo(f'Couldn\'t update config, field {field} is invalid.')
                return

        # make config update
        configs.header.columns = order_format
        click.echo('Updated fields.')
        configs.save()


config.add_command(header)
