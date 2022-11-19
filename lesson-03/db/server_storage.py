import datetime

from .db_connect import session, engine
from .db_client import DbClient
from .db_history import DbHistory
from .db_clients_online import DbClientsOnline


DbClient.metadata.create_all(engine)
DbHistory.metadata.create_all(engine)
DbClientsOnline.metadata.create_all(engine)


class ServerStorage:

    def get_user(self, user):
        pass

    def add_user(self, user):
        pass

    def register_user_online(self, user):
        pass

    def unregister_user_online(self, user):
        pass

    def register_user_action(self, user, action, info):
        pass


if __name__ == '__main__':
    client = DbClient('kto', 'admin')
    session.add(client)
    session.commit()

    history = DbHistory(client.id, datetime.datetime.now(), '127.0.0.1')
    client_online = DbClientsOnline(client.id, '127.0.0.1')
    session.add(history)
    session.add(client_online)
    session.commit()



