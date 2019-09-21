import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
"""AC imports"""
from autochannel.data.models import Guild, Category

class DB:
    def __init__(self):
        self.engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URI'))

    def session(self):
        return Session(self.engine)

