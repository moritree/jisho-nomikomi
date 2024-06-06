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
Generate a card for each of the cached tokens (corresponding to a given index).  
With no arguments, generate for all.

### `tokenise [TEXT]...`
*(`tokenize` is also accepted spelling)*

Collect and cache tokens from the given Japanese text.

### `library`
View the current cached 'library' of generated cards.

### `export [OPTIONS]`
Export the cached library to a csv file.

## Installation
To test the CLI, you can make a new virtualenv and then install the package. From a terminal within the project folder:
```
python -m venv .venv
. .venv/bin/activate
pip install --editable .
```
