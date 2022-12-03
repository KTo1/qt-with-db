from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from db_connect import Base


class DbHistory(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'))
    date_action = Column(DateTime)
    action = Column(String)
    info = Column(String)

    def __init__(self, client_id, date_action, action, info):
        self.client_id = client_id
        self.date_action = date_action
        self.action = action
        self.info = info

    def __repr__(self):
        return f'< {self.client_id}, {self.date_action}, {self.action}, {self.info}>'