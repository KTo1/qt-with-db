from sqlalchemy import Column, Integer, ForeignKey
from server_app.db.db_connect import Base


class DbStat(Base):
    __tablename__ = 'stat'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'))
    sent = Column(Integer)
    recv = Column(Integer)

    def __init__(self, client_id):
        self.client_id = client_id

    def __repr__(self):
        return f'< {self.client_id}, {self.sent}, {self.recv}>'