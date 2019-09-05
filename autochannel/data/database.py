import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from autochannel.data.models import Guild, Category


class DB:
    def __init__(self):
        self.engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URI'))

    def session(self):
        return Session(self.engine)

# db = DB()
# session = db.session()
# guild = session.query(Guild).get(321048288574963722)
# print(guild)
# cats = session.query(Category).with_entities(Category.id, Category.enabled, Category.prefix).filter_by(guild_id=321048288574963722).all()
# print(cats)
# session.close()


# cats = list(Category.query.with_entities(Category.id).filter_by(guild_id=guild_id).all())
