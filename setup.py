from setuptools import setup

setup(
    name='application',
    version='0.1.0',
    py_modules=['application', 'formatting', 'output'],
    install_requires=[
        'Click', 'jisho-api'
    ],
    entry_points={
        'console_scripts': [
            'word_card = application:word_card',
        ],
    },
)

# python3 -m venv .venv
# . .venv/bin/activate
# pip install --editable .

# run the last line again when command names are changed/added/etc
