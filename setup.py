from setuptools import setup

setup(
    name='jisho-nomikomi',
    version='0.1.0',
    py_modules=['application', 'formatting', 'output', 'reading'],
    install_requires=[
        'Click', 'jisho-api'
    ],
    entry_points={
        'console_scripts': [
            'word = application:cards_from_words',
            'tokenise = application:tokens',
            'tokenize = application:tokens',
        ],
    },
)

# python3 -m venv .venv
# . .venv/bin/activate
# pip3 install --editable .

# run the last line again when command names are changed/added/etc
