from sqlalchemy import Column, Integer, String, ForeignKey
from db_connect import Base


class DbClientsOnline(Base):
    __tablename__ = 'clients_online'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'))
    info = Column(String)

    def __init__(self, client_id, info):
        self.client_id = client_id
        self.info = info

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.id, self.client_id, self.info)