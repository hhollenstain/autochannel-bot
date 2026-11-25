"""Re-export of the shared models from the ``autochannel_models`` package.

The schema is defined only in ``packages/autochannel-models``; this module keeps
``autochannel.data.models`` importable for existing bot code and tests.
"""

from __future__ import annotations

from autochannel_models import Base, Category, Channel, Guild, db

__all__ = ["Base", "Channel", "Category", "Guild", "db"]
