"""AutoChannel database models.

This is the single source of truth for the schema shared by autochannel-ui and
autochannel-bot. It is plain SQLAlchemy (no Flask) so either service can import
it. Any change here must ship with an Alembic revision in ``migrations/versions``.
"""
from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Channel(Base):
    __tablename__ = 'channel'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('category.id'), nullable=False)
    chan_type: Mapped[str] = mapped_column(String(10), nullable=False, default='voice')
    num_suffix: Mapped[int] = mapped_column(Integer, nullable=False)

    category: Mapped['Category'] = relationship(back_populates='channels')

    def __repr__(self):
        return f'Channel({self.id})'


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('guild.id'), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    prefix: Mapped[str] = mapped_column(String(100), nullable=False, default='AC!')
    empty_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    channel_size: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    custom_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    custom_prefix: Mapped[str] = mapped_column(String(10), nullable=False, default='VC!')

    guild: Mapped['Guild'] = relationship(back_populates='categories')
    channels: Mapped[list[Channel]] = relationship(
        back_populates='category', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'Category({self.id})'

    def get_channels(self):
        return [channel.id for channel in self.channels]

    def get_chan_suffix(self):
        return [channel.num_suffix for channel in self.channels]

    def to_dict(self):
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

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    categories: Mapped[list[Category]] = relationship(
        back_populates='guild', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'Guild({self.id})'

    def get_categories(self):
        return {category.id: category.to_dict() for category in self.categories}
