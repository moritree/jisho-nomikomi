import csv
import io

from jisho_api.sentence.cfg import SentenceConfig
from jisho_api.word.cfg import WordConfig
from configuration import Config

DEFINITION_SEPARATOR_STR = '; '
TYPE_SEPARATOR_STR = ', '


def word_japanese(word: WordConfig) -> str:
    """Returns the primary written form of this word - kana if no kanji is available"""
    return word.japanese[0].word or word.japanese[0].reading


def get_field(word: WordConfig, field: str, senses: int, example: SentenceConfig = None) -> str:
    """Returns the correct field value for the supplied word."""
    # check valid field name
    if field not in Config.HeaderConfig.VALID_FIELDS:
        raise ValueError(f'Field {field} not in {Config.HeaderConfig.VALID_FIELDS}')

    # sublist of senses list according to n sought
    sense_count = word.senses.__len__()
    sublist = word.senses[:min(senses, sense_count - 1)] if senses > 0 else word.senses

    match field:
        case 'vocab':
            return word.japanese[0].word or word.japanese[0].reading
        case 'kana':
            return '' if not word.japanese[0].word else word.japanese[0].reading
        case 'translation':
            if senses == 1 or sense_count == 1:
                return DEFINITION_SEPARATOR_STR.join(word.senses[0].english_definitions)
            # one string with <br> separating sense definitions
            return '<br>'.join([f'({(word.senses.index(line) + 1).__str__()}) '
                                + DEFINITION_SEPARATOR_STR.join(line.english_definitions)
                                for line in sublist])
        case 'part_of_speech':
            if senses == 1 or sense_count == 1:
                return TYPE_SEPARATOR_STR.join(word.senses[0].parts_of_speech)
            # one string with <br> separating parts of speech, corresponding to sense definitions
            return '<br>'.join([f'({(word.senses.index(line) + 1).__str__()}) '
                                + TYPE_SEPARATOR_STR.join(line.parts_of_speech)
                                for line in sublist])
        case 'jlpt_level':
            if word.jlpt.__len__() > 0:
                return word.jlpt[0][-2:].upper()
        case 'tags':
            return ' '.join(word.tags)
        case 'example':
            return '' if not example else f'{example.japanese}<br>{example.en_translation}'
        case _:
            raise ValueError(f'Field {field} not in {Config.HeaderConfig.VALID_FIELDS}')


def csv_header(config: Config) -> str:  # Anki header data
    """Returns a `#key:value` formatted Anki file header based on configured values."""
    header_data = {}

    for key, value in config.header.__dict__.items():
        if key == '_fields':
            header_data['columns'] = ', '.join(value)
        elif value:
            if isinstance(value, list):
                # space separated list items in header
                header_data[key] = ' '.join(value)
            else:
                header_data[key] = value
    return '\n'.join([f'#{item[0]}:{item[1]}' for item in header_data.items()]) + '\n'


def word_to_csv(item: WordConfig, config: Config, example: SentenceConfig = None) -> str:
    """Converts a word into a CSV row for an Anki card."""
    out = io.StringIO()  # StringIO not str, for csv writer
    writer = csv.writer(out, dialect='unix')
    fields = []
    for f in config.header.fields:
        fields.append(get_field(item, f, config.senses, example))
    writer.writerow(fields)
    out.seek(0)
    return out.read()
