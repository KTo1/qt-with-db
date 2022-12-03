from sqlalchemy import Column, Integer, String, ForeignKey
from db_connect import Base


class DbContacts(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'))
    contact_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'))
    info = Column(String)

    def __init__(self, client_id, contact_id, info=''):
        self.client_id = client_id
        self.contact_id = contact_id
        self.info = info

    def __repr__(self):
        return f'id: {self.id}, client_id: {self.client_id}, contact_id: {self.contact_id}'