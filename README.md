# jisho-nomikomi 👹 辞書・飲み込み
A command line tool for generating Anki cards with information from [jisho.org](https://jisho.org/) (an online Japanese dictionary).

> **辞書・飲み込み → jisho nomikomi → dictionary swallowing**
>
> I wanted a cute name that's fun to say in my head.
> I like to imagine this program greedily scraping up data like a dubious little creature, and crunch-crunching it into a tidy little format.

# Usage ⚙️ 使い方
## Commands
You can run any command with the option `--help` for documentation.
### `word [OPTIONS] [WORDS]...`
Generate and cache cards for each of the given words.

### `token [OPTIONS] [INDICES]...`
Identify the tokens in a Japanese text, and generate cards for those you select.

### `library`
View the current cached 'library' of generated cards.

#### `library export [OPTIONS]`
Export the cached library to a csv file.

### `config`
#### `config view`
View the current config settings.

#### `config deck [DECK]`
Define the deck file header item.

#### `config tags [ALL_TAGS]...`
Define the tags header item (tags to be applied to every card on import).

#### `config fields [OPTIONS] [FIELDS]...`
Define the fields to be generated for each card.
- The option `-v` will display a list of all valid field types.

## Installation
To test the CLI, you can make a new virtualenv and then install the package. From a terminal within the project folder:
```
python -m venv .venv
. .venv/bin/activate
pip install --editable .
```
