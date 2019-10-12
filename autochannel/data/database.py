import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
"""AC imports"""
from autochannel.data.models import Guild, Category

class DB:
    def __init__(self):
        self.engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URI'))

    def session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

