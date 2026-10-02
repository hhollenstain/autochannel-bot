"""AutoChannel-Bot lives on
https://github.com/hhollenstain/autochannel-bot
"""

import re
from pathlib import Path

from setuptools import find_packages, setup

_INIT = Path(__file__).parent / "autochannel" / "__init__.py"
_VERSION = re.search(
    r"^VERSION_INFO:.*?\((\d+),\s*(\d+),\s*(\d+)\)",
    _INIT.read_text(encoding="utf-8"),
    re.MULTILINE,
)
if _VERSION is None:
    raise RuntimeError(f"VERSION not found in {_INIT}")
VERSION = f"{_VERSION.group(1)}.{_VERSION.group(2)}.{_VERSION.group(3)}"

INSTALL_REQUIREMENTS = [
    "aiohttp>=3.11.0",
    "aiomeasures>=0.5.0",
    "coloredlogs>=15.0.0",
    "dblpy>=0.4.0",
    "discord-py>=2.3.2",
    "flask-sqlalchemy>=3.1.0",
    "profanityfilter>=2.0.0",
    "prometheus-client>=0.21.0",
    "psycopg2-binary>=2.9.0",
    "pyyaml>=6.0",
    "requests>=2.32.0",
    "sqlalchemy>=2.0.25",
]

TEST_REQUIREMENTS = {
    "test": [
        "pytest>=8.3.0",
        "pytest-asyncio>=0.25.0",
        "ruff>=0.9.0",
    ],
    "dev": [
        "ruff>=0.9.0",
        "mypy>=1.14.0",
        "types-psycopg2>=2.9.0",
        "types-PyYAML>=6.0",
        "setuptools>=75.0.0",
    ],
}

setup(
    name="autochannel",
    version=VERSION,
    description="AutoChannel Discord Bot",
    url="https://github.com/hhollenstain/autochannel-bot",
    packages=find_packages(),
    include_package_data=True,
    install_requires=INSTALL_REQUIREMENTS,
    extras_require=TEST_REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "autochannel = autochannel.autochannel_bot:main",
        ],
    },
    python_requires=">=3.12",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
