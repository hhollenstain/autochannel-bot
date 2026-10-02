"""AutoChannel Discord Bot."""

from __future__ import annotations

import logging

VERSION_INFO: tuple[int, int, int] = (9, 3, 0)
VERSION: str = "9.3.0"
__version__: str = VERSION
__author__: str = "Henry Hollenstain"
__email__: str = "henry@hollenstain.io"

log: logging.Logger = logging.getLogger(__name__)
"""Logger for the autochannel package."""
