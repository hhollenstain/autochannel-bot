"""AutoChannel database models.

This is the single source of truth for the schema shared by the bot (apps/bot) and the
dashboard (apps/ui). It is plain SQLAlchemy (no Flask) so either service can import it.
Any change here must ship with an Alembic revision in ``migrations/versions``.
"""

from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _snowflake_pk() -> BigInteger:
    """BIGINT primary key that still autoincrements on SQLite (used by the test suites).

    Postgres DDL is unchanged: the variant only applies to the sqlite dialect.
    """
    return BigInteger().with_variant(Integer(), 'sqlite')


class Channel(Base):
    __tablename__ = 'channel'

    id: Mapped[int] = mapped_column(_snowflake_pk(), primary_key=True)
    cat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('category.id'), nullable=False)
    chan_type: Mapped[str] = mapped_column(String(10), nullable=False, default='voice')
    num_suffix: Mapped[int] = mapped_column(Integer, nullable=False)

    category: Mapped[Category] = relationship(back_populates='channels')

    def __repr__(self) -> str:
        return f'Channel({self.id})'


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(_snowflake_pk(), primary_key=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('guild.id'), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    prefix: Mapped[str] = mapped_column(String(100), nullable=False, default='AC!')
    empty_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    channel_size: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    custom_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    custom_prefix: Mapped[str] = mapped_column(String(10), nullable=False, default='VC!')

    guild: Mapped[Guild] = relationship(back_populates='categories')
    channels: Mapped[list[Channel]] = relationship(
        back_populates='category', cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f'Category({self.id})'

    def get_channels(self) -> list[int]:
        return [channel.id for channel in self.channels]

    def get_chan_suffix(self) -> list[int]:
        return [channel.num_suffix for channel in self.channels]

    def to_dict(self) -> dict[str, str | bool | int]:
        return {
            'prefix': self.prefix,
            'enabled': self.enabled,
            'channel_size': self.channel_size,
            'empty_count': self.empty_count,
            'custom_enabled': self.custom_enabled,
            'custom_prefix': self.custom_prefix,
        }


class Guild(Base):
    __tablename__ = 'guild'

    id: Mapped[int] = mapped_column(_snowflake_pk(), primary_key=True)

    categories: Mapped[list[Category]] = relationship(
        back_populates='guild', cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f'Guild({self.id})'

    def get_categories(self) -> dict[int, dict[str, str | bool | int]]:
        return {category.id: category.to_dict() for category in self.categories}
