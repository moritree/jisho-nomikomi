# jisho-nomikomi 👹 辞書・飲み込み
A command line tool for generating [Anki](https://apps.ankiweb.net/) cards 
with information from [jisho.org](https://jisho.org/) (an online Japanese dictionary).

> **辞書・飲み込み → jisho nomikomi → dictionary swallowing**
>
> I wanted a cute name that's fun to say in my head.
> I like to imagine this program greedily scraping up data like a dubious little creature, 
> and crunch-crunching it into a tidy little format.

# Usage ⚙️ 使い方
## Installation
To use the CLI, you can make a new virtualenv and then install the package. From a terminal within the project folder:
```
python -m venv .venv
. .venv/bin/activate
pip install --editable .
```

## Commands
You can run any command with the option `--help` for documentation.

### generation
- `token [OPTIONS] [TEXT]...` &ndash; identify the tokens in a Japanese text, and cache information for those you select.
- `word [OPTIONS] [WORDS]...` &ndash; generate and cache information for each of the given words

### library
- `library export [OPTIONS]` &ndash; export the cached library to a csv file, 
  according to the format described in the config file
- `library view` &ndash; view the current cached library of generated cards

### config
- `config header` &ndash; configuring fields to be written in the 
  [Anki header file](https://docs.ankiweb.net/importing/text-files.html#file-headers) on export. \
  All fields have the flag option `-rm` to remove the field from the header entirely, instead of updating values.
  - `config header columns [OPTIONS] [ORDER_FORMAT]...` &ndash; what each exported .csv column corresponds to
    - The option `-v` displays a list of all valid column field types.
    - Will regenerate library cache data with updated fields.
  - `config header deck [TITLE]` &ndash; presets the deck to import into, if it exists
  - `config header tags [ALL_TAGS]...` &ndash; list of tags, separated by spaces, to be applied to every card on import
- `config senses` &ndash; configure the (maximum) number of senses of a word to include in a card
- `config view` &ndash; view the current config settings.
