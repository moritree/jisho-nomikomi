from setuptools import setup

setup(
    name='jisho-nomikomi',
    version='0.1.0',
    py_modules=['application', 'formatting', 'output', 'reading', 'config'],
    install_requires=[
        'Click', 'jisho-api'
    ],
    entry_points={
        'console_scripts': [
            'word = application:word',
            'token = application:token',
            'tokenise = application:tokenise',
            'tokenize = application:tokenise',
            'library = application:library',
            'export-cards = application:export',
            'config = application:config',
        ],
    },
)

# python3 -m venv .venv
# . .venv/bin/activate
# pip3 install --editable .

# run the last line again when command names are changed/added/etc
