import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DB:
    def __init__(self):
        self.engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URI'))
        self._session_factory = sessionmaker(bind=self.engine)

    def session(self):
        return self._session_factory()

