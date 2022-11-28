from sqlalchemy import Column, Integer, String, DateTime
from db_connect import Base


class DbMessages(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    date_action = Column(DateTime)
    login_from = Column(String)
    login_to = Column(String)
    message = Column(String)

    def __init__(self, date_action, login_from, login_to, message):
        self.date_action = date_action
        self.login_from = login_from
        self.login_to = login_to
        self.message = message

    def __repr__(self):
        return f'from: {self.login_from}, to: {self.login_to}, mes: {self.message}'