"""``AutoChannel-Bot`` lives on
https://github.com/hhollenstain/autochannel-bot
"""
from setuptools import find_packages, setup

import autochannel

INSTALL_REQUIREMENTS = [
    'aiohttp>=3.9',
    'better-profanity>=0.7',
    'coloredlogs>=15.0',
    'discord.py>=2.5.0,<2.6',
    'flask_sqlalchemy>=3.1.0',
    'prometheus_client>=0.20',
    'psycopg[binary]>=3.1,<4',
    'pyyaml>=6.0',
    'requests>=2.31',
    'sqlalchemy>=2.0.30,<3',
    'topggpy>=1.4.0',
]

TEST_REQUIREMENTS = {
    'test': [
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
    python_requires='>=3.12',
    install_requires=INSTALL_REQUIREMENTS,
    extras_require=TEST_REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'autochannel = autochannel.autochannel_bot:main',
        ],
    },
)
