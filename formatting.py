import csv
import io
from functools import reduce

from jisho_api.word.cfg import WordConfig
from jisho_api.word.request import WordRequest

from config import load_json

CSV_DIALECT = 'unix'
VALID_FIELDS = ['vocab', 'kana', 'translation', 'part_of_speech', 'jlpt_level', 'example']
DEFINITION_SEPARATOR_STR = '; '
TYPE_SEPARATOR_STR = ', '


def word_formatted(word: WordRequest, csv_format: list[str], senses: int) -> list[str]:
    """Returns list of formatted fields for the given word, in the order of csv_format"""
    it_list = []
    for field in csv_format:
        it_list.append(get_field(word, field, senses))

    return it_list


def char_separated_str(ss: list[str], separator: str) -> str:
    if ss.__len__() == 0:
        return ""
    if ss.__len__() == 1:
        return ss[0]
    return reduce(lambda x, y: x + separator + y, ss)


def get_field(word: WordRequest, field: str, senses: int) -> str:
    """Returns the correct field value for the supplied word."""
    # check valid field name
    if field not in VALID_FIELDS:
        raise ValueError(f'Field {field} not in {VALID_FIELDS}')

    # sublist of senses list according to n sought
    sense_count = word.data[0].senses.__len__()
    sublist = word.data[0].senses[:min(senses, sense_count - 1)] if senses > 0 \
        else word.data[0].senses

    match field:
        case 'vocab':
            return word.data[0].japanese[0].word
        case 'kana':
            return word.data[0].japanese[0].reading
        case 'translation':
            if senses == 1 or sense_count == 1:
                return char_separated_str(word.data[0].senses[0].english_definitions, DEFINITION_SEPARATOR_STR)
            # one string with <br> separating sense definitions
            return '<br>'.join([f'({(word.data[0].senses.index(line) + 1).__str__()}) '
                           + char_separated_str(line.english_definitions, DEFINITION_SEPARATOR_STR)
                           for line in sublist])
        case 'part_of_speech':
            if senses == 1 or sense_count == 1:
                return char_separated_str(word.data[0].senses[0].parts_of_speech, TYPE_SEPARATOR_STR)
            # one string with <br> separating parts of speech, corresponding to sense definitions
            return '<br>'.join([f'({(word.data[0].senses.index(line) + 1).__str__()}) '
                                + char_separated_str(line.parts_of_speech, TYPE_SEPARATOR_STR)
                                for line in sublist])
        case 'jlpt_level':
            if word.data[0].jlpt.__len__() > 0:
                return word.data[0].jlpt[0][-2:].upper()
        case _:
            # this field may be populated later, but cannot be filled from the WordRequest data, so empty
            return ''


def csv_header() -> str:  # Anki header data
    """Returns a `#key:value` formatted Anki file header based on configured values."""
    header_data = {'separator': 'comma'}
    header_data.update(load_json() or {})

    # space separated list items in header
    for key, value in header_data.items():
        if isinstance(value, list):
            header_data[key] = ' '.join(value)

    return '\n'.join([f'#{item[0]}:{item[1]}' for item in header_data.items()]) + '\n'


def csv_formatted_item(item: list[str]) -> str:
    """Returns the item formatted as a valid row to write to a .csv file."""
    out = io.StringIO()
    writer = csv.writer(out, dialect=CSV_DIALECT)
    writer.writerow(item)
    out.seek(0)
    return out.read()


def word_config_dict(word: WordConfig):
    return {
        'slug': word.slug,
        'is_common': word.is_common,
        'tags': word.tags,
        'jlpt': word.jlpt,
        'japanese': [{
            'word': ja.word,
            'reading': ja.reading
        } for ja in word.japanese],
        'senses': [{
            'english': sense.english_definitions,
            'parts_of_speech': sense.parts_of_speech,
            'tags': sense.tags,
            'restrictions': sense.restrictions,
            'see_also': sense.see_also,
            'antonyms': sense.antonyms,
            'source': sense.source,
            'info': sense.info
        } for sense in word.senses]
    }
