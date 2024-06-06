from functools import reduce
from jisho_api.word.request import WordRequest

CSV_DIALECT = 'unix'
VALID_FIELDS = ['vocab', 'kana', 'translation', 'part_of_speech', 'jlpt_level']
DEFINITION_SEPARATOR_STR = '; '
TYPE_SEPARATOR_STR = ', '


def word_formatted(word: WordRequest, csv_format: list[str], senses: int) -> list[str]:
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
    sense_count = word.data[0].senses.__len__()
    # sublist of senses list according to n sought
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
            return reduce(lambda x, y: x + '<br>' + y,
                          # each sense mapped to the format "def; def; ..."
                          [f'({(word.data[0].senses.index(line) + 1).__str__()}) '
                           + char_separated_str(line.english_definitions, DEFINITION_SEPARATOR_STR)
                           for line in sublist])
        case 'part_of_speech':
            if senses == 1 or sense_count == 1:
                return char_separated_str(word.data[0].senses[0].parts_of_speech, TYPE_SEPARATOR_STR)
            # one string with <br> separating parts of speech, corresponding to sense definitions
            return reduce(lambda x, y: x + '<br>' + y,
                          # each sense mapped to the format "def; def; ..."
                          [f'({(word.data[0].senses.index(line) + 1).__str__()}) '
                           + char_separated_str(line.parts_of_speech, TYPE_SEPARATOR_STR)
                           for line in sublist])
        case 'jlpt_level':
            if word.data[0].jlpt.__len__() > 0:
                return word.data[0].jlpt[0][-2:].upper()
        case _:
            raise RuntimeError('Unknown field: ' + field)


def csv_header(tags: str = None, deck: str = None) -> str:  # Anki header data
    header_data = {
        'separator': 'comma'
    }
    if deck:
        header_data.update({'deck': deck})
    if tags:
        header_data.update({'tags': tags})

    return reduce(lambda a, b: a + '\n' + b, [f'#{item[0]}: {item[1]}' for item in header_data.items()]) + '\n'
