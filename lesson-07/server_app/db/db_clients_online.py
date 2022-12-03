from sqlalchemy import Column, Integer, String, ForeignKey
from server_app.db.db_connect import Base


class DbClientsOnline(Base):
    __tablename__ = 'clients_online'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'))
    ip_address = Column(String)
    port = Column(String)
    info = Column(String)

    def __init__(self, client_id, ip_address, port, info):
        self.client_id = client_id
        self.ip_address = ip_address
        self.port = port
        self.info = info

    def __repr__(self):
        return f'client_id: {self.client_id}, info: { self.info}'