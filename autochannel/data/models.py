from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BigInteger, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

__all__ = ["Channel", "Category", "Guild", "db"]


class Channel(db.Model):
    """Database model for voice channels."""

    __tablename__ = "channel"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cat_id: Mapped[int] = mapped_column(BigInteger, db.ForeignKey("category.id"), nullable=False)
    chan_type: Mapped[str] = mapped_column(String(10), default="voice", nullable=False)
    num_suffix: Mapped[int] = mapped_column(Integer, nullable=False)

    category: Mapped[Category] = relationship("Category", back_populates="channels")

    def __repr__(self) -> str:
        return (
            f"Channel(id={self.id}, cat_id={self.cat_id}, "
            f"chan_type='{self.chan_type}', num_suffix={self.num_suffix})"
        )


class Category(db.Model):
    """Database model for voice channel categories."""

    __tablename__ = "category"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, db.ForeignKey("guild.id"), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    prefix: Mapped[str] = mapped_column(String(10), default="AC!", nullable=False)
    empty_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    channel_size: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    custom_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    custom_prefix: Mapped[str] = mapped_column(String(10), default="VC!", nullable=False)
    guild: Mapped[Guild] = relationship("Guild", back_populates="categories")
    channels: Mapped[list[Channel]] = relationship("Channel", back_populates="category")

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

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    categories: Mapped[list[Category]] = relationship("Category", back_populates="guild")

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
