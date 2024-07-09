import os
import click
from jisho_api.sentence import Sentence
from jisho_api.tokenize import Tokens
from jisho_api.word import Word
from jisho_api.word.cfg import WordConfig

from configuration import CACHE_DIR, CONFIG_FILENAME, LIBRARY_FILENAME, get_config, VALID_FIELDS, \
    get_library, LibraryCache, get_examples
from formatting import word_to_csv, csv_header, word_japanese


def gen_words(words: list[str]):
    """Get and cache info on each word in the provided list of words."""
    got = list(w.data[0] for w in filter(lambda x: x is not None, [Word.request(w) for w in words]))
    click.echo(f'Found {', '.join([c.slug for c in got])}')

    library_cache: LibraryCache = get_library()
    for c in got:
        library_cache.cards.append(c)
    library_cache.save()
    click.echo('Added to library.')


@click.command('word')
@click.argument('words', nargs=-1)
def word(words):
    """
    Create a card from the jisho.org entry on each of WORDS.
    This can be in English or Japanese (kanji, kana, romaji).
    """
    # words may be split by Japanese space character,
    # in which case they won't be separated. so, we do it ourselves
    ww: list[str] = sum([w.split('\u3000') for w in words], [])

    gen_words(ww)


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
@click.option('-in', '--indices', is_flag=True, default=False, help='Display cards with indices')
def view(indices):
    """Echo information on the current cached library of words."""
    result = get_library()
    click.echo(', '.join([(f'[{result.cards.index(c)}] ' if indices else '') + word_japanese(c) for c in result.cards])
               if result.cards.__len__() > 0 else 'No cached cards.')


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

    # gather card data
    library_cache = get_library()
    configs = get_config()
    examples = get_examples()

    # write export
    output_file.write(csv_header(configs))
    for row in [word_to_csv(c, configs, examples.examples.get(c.slug)) for c in library_cache.cards]:
        output_file.write(row)

    # clear cache
    if clear_after_export:
        click.echo(f'Clearing library cache...')
        os.remove(CACHE_DIR / LIBRARY_FILENAME)
        click.echo('Done.')


@library.command()
@click.argument('words', nargs=-1)
@click.option('-in', '--indices', is_flag=True, default=False,
              help='Take list of (zero indexed) indices for words to delete from the library, instead of whole words')
def delete(words, indices):
    if not words:
        click.echo('Specify words to delete.')
        return

    library_cache = get_library()
    removed: list[str] = []
    not_found: list[str] = []
    for w in sum([w.split('\u3000') for w in words], []):
        if not indices:
            match = list(filter(lambda x: x == word_japanese(w), library_cache.cards))
            if match:
                removed.append(word_japanese(match[0]))
                library_cache.cards.remove(match[0])
            else:
                not_found.append(w)
        else:
            if not w.isdigit() or int(w) >= library_cache.cards.__len__() or int(w) < 0:
                click.echo(f'Invalid index: {w}')
                break
            removed.append(word_japanese(library_cache.cards[int(w)]))
            library_cache.cards.remove(library_cache.cards[int(w)])

    if removed:
        click.echo(f'Removed {', '.join(removed)} from library.')
        if not_found:
            click.echo(f'Couldn\'t find {', '.join(not_found)}, so not removed.')
        library_cache.save()
    else:
        click.echo('Couldn\'t find any matching words to delete.')


@library.command()
@click.argument('words', nargs=-1)
@click.option('-cf', '--choose-first', is_flag=True, default=False,
              help='Automatically choose the first available example sentence.')
@click.option('-ow', '--overwrite', is_flag=True, default=False,
              help='Overwrite existing examples.')
@click.option('-n', '--num-options', type=int, default=5,
              help='(Maximum) Number of example sentences to offer as options.')
def example(words, choose_first, overwrite, num_options):
    """Warning: Sentence scraping API often returns incomplete sentences. Read carefully before choosing."""
    library_cache = get_library()

    # get matching words from library
    match: list[WordConfig] = []
    if words:
        for w in words:
            matched = list(filter(lambda x: w == word_japanese(x), library_cache.cards))
            if matched:
                match += matched
            else:
                click.echo(f'Couldn\'t find "{w}" in library')
    # get all words if none specified
    else:
        match = library_cache.cards
    # can't do much with no words
    if not match:
        click.echo('No matching words in library')
        return

    examples = get_examples()

    # don't try to get examples for cards that already have them (unless we're overwriting)
    if not overwrite:
        match = list(filter(lambda x: not examples.examples.get(x.slug), match))

    # process sentence requests for each word
    for w in match:
        requests = Sentence.request(w.slug).data[:num_options]  # capped

        # user chooses index of sentence to add
        i = 0
        if not choose_first:
            i = None
            click.echo(f'Example sentences for {word_japanese(w)}:\n'
                       f'{'\n'.join([f'({i})\t{r.japanese} ({r.en_translation})' for i, r in enumerate(requests)])}')
            # get user input, keep asking until they give a valid integer
            while not i:
                i = click.prompt('Please enter the index for the example sentence you want to include', type=int)
                if i >= len(requests):
                    click.echo(f'Index {i} out of bounds for range [0, {len(requests)})')
                    i = None
        # update examples object
        examples.examples.update({w.slug: requests[i]})
    # save to disk
    click.echo(f'{match.__len__()} examples updated.')
    examples.save()


@click.group('config')
@click.pass_context
def config(ctx):
    return


@config.command()
def view():
    """View the current config options."""
    click.echo(get_config().__str__() or 'No config file to view.')


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
@click.argument('sense-count', nargs=1, type=int)
@click.option('-rm', '--remove', is_flag=True, default=False, help='')
def senses(sense_count, remove):
    """The (max) number of senses to export for each word."""
    configs = get_config()
    configs.senses = None if remove else sense_count
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
    configs = get_config()
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
    configs = get_config()
    if remove:
        configs.header.deck = None
    elif title:
        configs.header.deck = title
    configs.save()
    click.echo('Header deck updated.')


@header.command()
@click.argument('order_format', nargs=-1)
@click.option('-v', '--valid-options', is_flag=True, default=False)
@click.option('-rm', '--remove', is_flag=True, default=False, help='Remove field from header')
def columns(order_format, valid_options, remove):
    """Update the fields list. If no values are specified, the field is removed."""
    # supply list of valid options
    if valid_options:
        click.echo(f'Valid field options: {VALID_FIELDS}')
        return

    configs = get_config()
    if remove:
        configs.header.tags = None
        configs.save()
    elif (not order_format) or order_format.__len__() < 2:
        # need at least two fields
        click.echo('No fields specified.')
    else:
        # try to write fields
        # check each provided field is valid
        for field in order_format:
            if field not in VALID_FIELDS:
                click.echo(f'Couldn\'t update config, field {field} is invalid.')
                return

        # make config update
        configs.header.columns = order_format
        click.echo('Updated fields.')
        configs.save()


config.add_command(header)
