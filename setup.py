"""``AutoChannel-Bot`` lives on
https://github.com/hhollenstain/autochannel-bot
"""
from setuptools import setup, find_packages
import autochannel

INSTALL_REQUIREMENTS = [
    # 'aiohttp==3.6.3',
    'aiohttp',
    'aiomeasures',
    'coloredlogs',
    'dblpy',
    'discord.py==2.3.2',
    'flask_sqlalchemy',
    'profanityfilter',
    'prometheus_client',
    'psycopg2-binary',
    'pyyaml',
    # 'requests==2.21.0',
    'requests',
    'sqlalchemy',
]

TEST_REQUIREMENTS = {
    'test':[
        'pytest',
        'pylint',
        'sure',
        ],
    'dev': [
        'ruff',
    ],
    }

setup(
    name='autochannel',
    version=autochannel.VERSION,
    description='AutoChannel Discord Bot',
    url='https://github.com/hhollenstain/autochannel-bot',
    packages=find_packages(),
    include_package_data=True,
    install_requires=INSTALL_REQUIREMENTS,
    extras_require=TEST_REQUIREMENTS,
    entry_points={
        'console_scripts':  [
            'autochannel = autochannel.autochannel_bot:main',
        ],
    },
    )
