from functools import reduce
from jisho_api.word.request import WordRequest

VALID_FIELDS = ['vocab', 'kana', 'translation', 'part_of_speech', 'jlpt_level']
DEFINITION_SEPARATOR_STR = "; "


def word_formatted(word: WordRequest, csv_format: list[str], senses: int) -> list[str]:
    it_list = []
    for field in csv_format:
        it_list.append(get_field(word, field, senses))

    return it_list


def char_separated_str(ss: list[str], separator: str) -> str:
    return reduce(lambda x, y: x + separator + y, ss)


def get_field(word: WordRequest, field: str, senses: int) -> str:
    match field:
        case 'vocab':
            return word.data[0].japanese[0].word
        case 'kana':
            return word.data[0].japanese[0].reading
        case 'translation':
            if senses == 1:
                return char_separated_str(word.data[0].senses[0].english_definitions, DEFINITION_SEPARATOR_STR)
            # one string with <br> separating sense definitions
            return reduce(lambda x, y: x + "<br>" + y,
                          # each sense mapped to the format "def; def; ..."
                          [char_separated_str(line.english_definitions, DEFINITION_SEPARATOR_STR)
                           # sublist of senses list according to n sought
                           for line in (word.data[0].senses[:senses] if senses > 0 else word.data[0].senses)])
        case 'part_of_speech':
            return word.data[0].senses[0].parts_of_speech.__str__()
        case 'jlpt_level':
            if word.data[0].jlpt.__len__() > 0:
                return word.data[0].jlpt[0][-2:].upper()
        case _:
            raise RuntimeError('Unknown field: ' + field)
