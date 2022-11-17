from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from .db_connect import Base


class DbHistory(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'))
    date_login = Column(DateTime)
    ip_address = Column(String)

    def __init__(self, client_id, date_login, ip_address):
        self.client_id = client_id
        self.date_login = date_login
        self.ip_address = ip_address

    def __repr__(self):
        return "<history('%s','%s', '%s')>" % (self.client_id, self.date_login, self.ip_address)