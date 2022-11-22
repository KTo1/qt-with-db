from sqlalchemy import Column, Integer, String
from db_connect import Base


class DbContacts(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    login = Column(String)
    info = Column(String)

    def __init__(self, login, info):
        self.login = login
        self.info = info

    def __repr__(self):
        return f'id: {self.id}, login>: {self.login}, last login: {self.info}'