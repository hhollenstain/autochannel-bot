"""AutoChannel-Bot lives on
https://github.com/hhollenstain/autochannel-bot
"""

from __future__ import annotations

import re
from pathlib import Path

from setuptools import find_packages, setup

_INIT = Path(__file__).parent / "autochannel" / "__init__.py"
_VERSION = re.search(
    r'^VERSION = ["\']([^"\']+)["\']',
    _INIT.read_text(encoding="utf-8"),
    re.MULTILINE,
)
if _VERSION is None:
    raise RuntimeError(f"VERSION not found in {_INIT}")

INSTALL_REQUIREMENTS = [
    "aiohttp>=3.9.0",
    "aiomeasures>=0.5.0",
    "coloredlogs>=15.0.0",
    "dblpy>=0.4.0",
    "discord.py>=2.4.0",
    "flask_sqlalchemy>=3.1.0",
    "profanityfilter>=2.0.0",
    "prometheus_client>=0.20.0",
    "psycopg2-binary>=2.9.0",
    "pyyaml>=6.0",
    "requests>=2.31.0",
    "SQLAlchemy>=2.0.0",
]

TEST_REQUIREMENTS = {
    "test": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.23.0",
        "ruff>=0.3.0",
    ],
    "dev": [
        "ruff>=0.3.0",
        "mypy>=1.8.0",
    ],
}

setup(
    name="autochannel",
    version=_VERSION.group(1),
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
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
    ],
)
