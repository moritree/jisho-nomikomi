import csv
import io
from functools import reduce

from jisho_api.word.cfg import WordConfig
from configuration import VALID_FIELDS, Config

CSV_DIALECT = 'unix'
DEFINITION_SEPARATOR_STR = '; '
TYPE_SEPARATOR_STR = ', '


def char_separated_str(ss: list[str], separator: str) -> str:
    if ss.__len__() == 0:
        return ""
    if ss.__len__() == 1:
        return ss[0]
    return reduce(lambda x, y: x + separator + y, ss)


def get_field(word: WordConfig, field: str, senses: int) -> str:
    """Returns the correct field value for the supplied word."""
    # check valid field name
    if field not in VALID_FIELDS:
        raise ValueError(f'Field {field} not in {VALID_FIELDS}')

    # sublist of senses list according to n sought
    sense_count = word.senses.__len__()
    sublist = word.senses[:min(senses, sense_count - 1)] if senses > 0 \
        else word.senses

    match field:
        case 'vocab':
            return word.japanese[0].word or word.japanese[0].reading
        case 'kana':
            return '' if not word.japanese[0].word else word.japanese[0].reading
        case 'translation':
            if senses == 1 or sense_count == 1:
                return char_separated_str(word.senses[0].english_definitions, DEFINITION_SEPARATOR_STR)
            # one string with <br> separating sense definitions
            return '<br>'.join([f'({(word.senses.index(line) + 1).__str__()}) '
                                + char_separated_str(line.english_definitions, DEFINITION_SEPARATOR_STR)
                                for line in sublist])
        case 'part_of_speech':
            if senses == 1 or sense_count == 1:
                return char_separated_str(word.senses[0].parts_of_speech, TYPE_SEPARATOR_STR)
            # one string with <br> separating parts of speech, corresponding to sense definitions
            return '<br>'.join([f'({(word.senses.index(line) + 1).__str__()}) '
                                + char_separated_str(line.parts_of_speech, TYPE_SEPARATOR_STR)
                                for line in sublist])
        case 'jlpt_level':
            if word.jlpt.__len__() > 0:
                return word.jlpt[0][-2:].upper()
        case 'tags':
            return ' '.join(word.tags)
        case _:
            # this field may be populated later, but cannot be filled from the WordRequest data, so empty
            return ''


def csv_header(config: Config) -> str:  # Anki header data
    """Returns a `#key:value` formatted Anki file header based on configured values."""
    header_data = {}

    for key, value in config.header.__dict__.items():
        if isinstance(value, list):
            # space separated list items in header
            header_data[key] = ' '.join(value)
        else:
            header_data[key] = value

    return '\n'.join([f'#{item[0]}:{item[1]}' for item in header_data.items()]) + '\n'


def word_to_csv(item: WordConfig, config: Config) -> str:
    out = io.StringIO()
    writer = csv.writer(out, dialect=CSV_DIALECT)
    cols = []
    for col in config.header.columns:
        cols.append(get_field(item, col, 1))
    writer.writerow(cols)
    out.seek(0)
    return out.read()
