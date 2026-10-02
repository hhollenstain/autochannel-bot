from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BigInteger, Boolean, Column, Integer, String
from sqlalchemy.orm import Relationship, relationship

db = SQLAlchemy()

db = SQLAlchemy()


class Channel(db.Model):
    """Database model for voice categories."""

    __tablename__ = "channel"

    id = Column(BigInteger, primary_key=True)
    cat_id = Column(BigInteger, db.ForeignKey("category.id"), nullable=False)
    chan_type = Column(String(10), default="voice", nullable=False)
    num_suffix = Column(Integer, nullable=False)

    category: Relationship[Category] = relationship("Category", back_populates="channels")


class Category(db.Model):
    """Database model for voice channel categories."""

    __tablename__ = "category"

    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, db.ForeignKey("guild.id"), nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
    prefix = Column(String(10), default="AC!", nullable=False)
    empty_count = Column(Integer, default=1, nullable=False)
    channel_size = Column(Integer, default=10, nullable=False)
    custom_enabled = Column(Boolean, default=False, nullable=False)
    custom_prefix = Column(String(10), default="VC!", nullable=False)
    channels: Relationship[Channel] = relationship("Channel", back_populates="category")

    def get_channels(self) -> list[int]:
        """Get list of channel IDs for this category.

        Returns:
            List of channel IDs.
        """
        return [channel.id for channel in self.channels]

    def get_chan_suffix(self) -> list[int]:
        """Get list of channel suffixes for this category.

        Returns:
            List of channel suffixes.
        """
        return [channel.num_suffix for channel in self.channels]


class Guild(db.Model):
    """Database model for Discord guilds."""

    __tablename__ = "guild"

    id = Column(BigInteger, primary_key=True)
    categories: Relationship[Category] = relationship("Category", back_populates="guild")

    def __repr__(self) -> str:
        return f"Guild({self.id})"

    def get_categories(self) -> dict[int, dict[str]]:
        """Get category configuration for this guild.

        Returns:
            Dictionary of category configurations.
        """
        cats: dict[int, dict[str]] = {}
        for category in self.categories:
            cats[category.id] = {
                "prefix": category.prefix,
                "enabled": category.enabled,
                "channel_size": category.channel_size,
                "empty_count": category.empty_count,
                "custom_enabled": category.custom_enabled,
                "custom_prefix": category.custom_prefix,
            }
        return cats
