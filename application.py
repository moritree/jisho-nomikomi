import os
import click
from jisho_api.sentence import Sentence
from jisho_api.tokenize import Tokens
from jisho_api.word import Word
from jisho_api.word.cfg import WordConfig

from configuration import Config, Examples, Library
from formatting import word_to_csv, csv_header, word_japanese


def gen_words(words: list[str]):
    """Get and cache info on each word in the provided list of words."""
    got = list(w.data[0] for w in filter(lambda x: x is not None, [Word.request(w) for w in words]))
    click.echo(f'Found {', '.join([c.slug for c in got])}')

    library_cache: Library = Library.get()
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
    result = Library.get()
    click.echo(', '.join([(f'[{result.cards.index(c)}] ' if indices else '') + word_japanese(c) for c in result.cards])
               if result.cards.__len__() > 0 else 'No cached cards.')


@library.command()
def clear():
    """Clear library cache."""
    if list(filter(lambda x: x is True,
                   [os.path.isfile(path) for path in [Library.PATH, Examples.PATH]])).__len__() == 0:
        click.echo('No library cache to clear.')
        return

    caches = Library, Examples
    if click.confirm('Are you sure you want to clear library?', abort=True):
        for cache in caches:
            cache.delete_file()


@library.command('export')
@click.option('-o', '--output-file', type=click.File('w'), default='out.csv')
@click.option('-c', '--clear', 'clear_after_export', is_flag=True, default=False,
              help='Clear library cache after exporting.')
def export(output_file, clear_after_export):
    """Export the current cached library to a CSV file."""
    # can't export from a nonexistent library
    if not os.path.isfile(Library.PATH):
        click.echo('No cached cards to export.')
        return

    # gather card data
    library_cache = Library.get()
    configs = Config.get()
    examples = Examples.get()

    # write export
    output_file.write(csv_header(configs))
    for row in [word_to_csv(c, configs, examples.examples.get(c.slug)) for c in library_cache.cards]:
        output_file.write(row)

    # clear cache
    if clear_after_export:
        click.echo(f'Clearing library cache...')
        os.remove(Library.PATH)
        click.echo('Done.')


@library.command()
@click.argument('words', nargs=-1)
@click.option('-in', '--indices', is_flag=True, default=False,
              help='Take list of (zero indexed) indices for words to delete from the library, instead of whole words')
def delete(words, indices):
    if not words:
        click.echo('Specify words to delete.')
        return

    library_cache = Library.get()
    removed: list[str] = []
    not_found: list[str] = []
    for w in sum([w.split('\u3000') for w in words], []):
        if not indices:
            match = list(filter(lambda x: w == word_japanese(x), library_cache.cards))
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
@click.option('-in', '--indices', is_flag=True, default=False,
              help='Take list of (zero indexed) indices instead of full words.')
@click.option('-cf', '--choose-first', is_flag=True, default=False,
              help='Automatically choose the first available example sentence. WARNING: Don\'t trust they\'ll be good.')
@click.option('-ow', '--overwrite', is_flag=True, default=False,
              help='Overwrite existing examples.')
@click.option('-n', '--num-options', type=int, default=5,
              help='(Maximum) Number of example sentences to offer as options.')
def example(words, choose_first, overwrite, num_options, indices):
    """ Generate examples to associate with the given words in the library.
    \nWARNING: The sentence scraping API often returns incomplete sentences.
    It's not my fault. Read carefully before choosing."""

    # get matching words from library
    library_cache = Library.get()
    match: list[WordConfig] = []
    if words:
        for w in words:
            if not indices:
                matched = list(filter(lambda x: w == word_japanese(x), library_cache.cards))
                if matched:
                    match += matched
                else:
                    click.echo(f'Couldn\'t find "{w}" in library')
            else:
                if not w.isdigit() or int(w) >= library_cache.cards.__len__() or int(w) < 0:
                    click.echo(f'Invalid index: {w}')
                    break
                match.append(library_cache.cards[int(w)])
    # get all words if none specified
    else:
        match = library_cache.cards
    # can't do much with no words
    if not match:
        click.echo('No matching words in library')
        return

    examples = Examples.get()

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
                       f'{'\n'.join([f'({i + 1})\t{r.japanese} ({r.en_translation})' 
                                     for i, r in enumerate(requests)])}')
            # get user input, keep asking until they give a valid integer
            while not i:
                i = click.prompt('Please enter the index for the example sentence you want to include',
                                 type=int, default=-1)

                if i > len(requests):
                    click.echo(f'Index {i} out of bounds for range [1, {len(requests)}]')
                    i = None
        # update examples object
        if i > 0:
            examples.examples.update({w.slug: requests[i]})
        elif overwrite:
            examples.examples.pop(w.slug, None)
    # save to disk
    click.echo(f'{match.__len__()} examples updated.')
    examples.save()


@click.group('config')
def config():
    return


@config.command()
def view():
    """View the current config options."""
    click.echo(Config.get().__str__() or 'No config file to view.')


@config.command()
def clear():
    """Clear config file."""
    if os.path.isfile(Config.PATH):
        if click.confirm('Are you sure you want to clear config file?', abort=True):
            os.remove(Config.PATH)
            click.echo('Config file cleared.')
    else:
        click.echo('No config file to clear.')


@config.command()
@click.argument('sense-count', nargs=1, type=int)
@click.option('-rm', '--remove', is_flag=True, default=False, help='')
def senses(sense_count, remove):
    """The (max) number of senses to export for each word."""
    configs = Config.get()
    configs.senses = None if remove else sense_count
    configs.save()
    click.echo('Senses value updated.')


@click.group('header')
def header():
    """Configure items for Anki file header."""
    return


@header.command()
@click.argument('all-tags', nargs=-1)
@click.option('-rm', '--remove', is_flag=True, default=False, help='Remove field from header')
def tags(all_tags, remove):
    """Update the tags list. For tags that will be automatically applied to each card on import."""
    configs = Config.get()
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
    configs = Config.get()
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
        click.echo(f'Valid field options: {Config.HeaderConfig.VALID_FIELDS}')
        return

    configs = Config.get()
    if remove:
        configs.header.tags = None
        configs.save()
    elif not order_format:
        # need at least two fields
        click.echo('No fields specified.')
    elif order_format.__len__() < 2:
        click.echo('Needs at least two fields.')
    else:
        # make config update
        try:
            configs.header.columns = order_format
            click.echo('Updated fields.')
            configs.save()
        except KeyError as e:
            click.echo(f'Couldn\'t update config: {e}')


config.add_command(header)
