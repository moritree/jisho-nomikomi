from jisho_api.word.request import WordRequest

VALID_FIELDS = ['vocab', 'kana', 'translation', 'part_of_speech', 'jlpt_level']


def word_formatted(word: WordRequest, csv_format: list[str]) -> list[str]:
    it_list = []
    # print(word)
    for field in csv_format:
        it_list.append(get_field(word, field))

    return it_list


def get_field(word: WordRequest, field: str) -> str:
    match field:
        case 'vocab':
            return word.data[0].japanese[0].word
        case 'kana':
            return word.data[0].japanese[0].reading
        case 'translation':
            return word.data[0].senses[0].english_definitions.__str__()
        case 'part_of_speech':
            return word.data[0].senses[0].parts_of_speech.__str__()
        case 'jlpt_level':
            if word.data[0].jlpt.__len__() > 0:
                return word.data[0].jlpt[0]
        case _:
            raise RuntimeError('Unknown field: ' + field)
