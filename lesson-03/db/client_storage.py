from sqlalchemy import update, select
from datetime import datetime
from db_connect import session, engine
from db_contacts import DbContacts
from db_messages import DbMessages


DbContacts.metadata.create_all(engine)
DbMessages.metadata.create_all(engine)


class ClientStorage:

    def clear_contacts(self):
        session.query(DbContacts).delete()
        session.commit()

if __name__ == '__main__':

    sto = ClientStorage()
