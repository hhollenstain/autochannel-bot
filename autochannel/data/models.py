from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BigInteger, Boolean, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base shared by the Flask-SQLAlchemy models.

    Note:
        All database operations should be performed within a transaction context
        to ensure proper commit/rollback behavior. Use the DB.transaction()
        context manager from autochannel.data.database for this purpose.

        Example:
            with db.transaction() as session:
                # Perform your database operations here
                category = Category(guild_id=123)
                session.add(category)
                # Commit happens automatically on success, rollback on error
    """


db = SQLAlchemy(model_class=Base)


def _snowflake_pk() -> BigInteger:
    """Primary key that autoincrements on SQLite and stays BIGINT on Postgres."""
    return BigInteger().with_variant(Integer(), "sqlite")


__all__ = ["Channel", "Category", "Guild", "db"]


class Channel(Base):
    """Database model for voice channels."""

    __tablename__ = "channel"

    id: Mapped[int] = mapped_column(_snowflake_pk(), primary_key=True)
    cat_id: Mapped[int] = mapped_column(BigInteger, db.ForeignKey("category.id"), nullable=False)
    chan_type: Mapped[str] = mapped_column(String(10), default="voice", nullable=False)
    num_suffix: Mapped[int] = mapped_column(Integer, nullable=False)

    category: Mapped[Category] = relationship("Category", back_populates="channels")

    def __repr__(self) -> str:
        return (
            f"Channel(id={self.id}, cat_id={self.cat_id}, "
            f"chan_type='{self.chan_type}', num_suffix={self.num_suffix})"
        )


class Category(Base):
    """Database model for voice channel categories."""

    __tablename__ = "category"

    id: Mapped[int] = mapped_column(_snowflake_pk(), primary_key=True)
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

    def save_with_transaction(self, session):
        """Save the category with explicit transaction handling.

        This method ensures that the category is properly added to
        the database within a transaction, committing on success or
        rolling back on failure.

        Args:
            session: The SQLAlchemy session to use for the transaction.

        Raises:
            Exception: If the save operation fails, it will be re-raised after rollback.
        """
        try:
            session.add(self)
            session.commit()
        except Exception:
            session.rollback()
            raise


class Guild(Base):
    """Database model for Discord guilds."""

    __tablename__ = "guild"

    id: Mapped[int] = mapped_column(_snowflake_pk(), primary_key=True)
    categories: Mapped[list[Category]] = relationship("Category", back_populates="guild")

    def __repr__(self) -> str:
        return f"Guild({self.id})"

    def get_categories(self) -> dict[int, dict[str, str | bool | int]]:
        """Get category configuration for this guild.

        Returns:
            Dictionary of category configurations.
        """
        cats: dict[int, dict[str, str | bool | int]] = {}
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
