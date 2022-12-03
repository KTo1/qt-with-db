from sqlalchemy import Column, Integer, String
from server_app.db.db_connect import Base


class DbClient(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    login = Column(String)
    pwd_hash = Column(String)
    info = Column(String)

    def __init__(self, login, pwd_hash, info):
        self.login = login
        self.info = info
        self.pwd_hash = pwd_hash

    def __repr__(self):
        return f'id: {self.id}, login: {self.login}, last login: {self.info}'