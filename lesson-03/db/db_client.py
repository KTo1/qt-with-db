from sqlalchemy import Column, Integer, String
from .db_connect import Base


class DbClient(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    login = Column(String)
    info = Column(String)

    def __init__(self, login, info):
        self.login = login
        self.info = info

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.id, self.login, self.info)