import datetime

from db_connect import session, engine
from db_client import DbClient
from db_history import DbHistory
from db_clients_online import DbClientsOnline


DbClient.metadata.create_all(engine)
DbHistory.metadata.create_all(engine)
DbClientsOnline.metadata.create_all(engine)


class ServerStorage:

    def get_client(self, client):
        data = session.query(DbClient).filter(DbClient.login == client).limit(1).first()
        return data.id if data else 0

    def add_client(self, client, info=''):
        client = DbClient(client, info)
        session.add(client)
        session.commit()

    def register_client_online(self, client_id, info):
        client_online = DbClientsOnline(client_id, info)
        session.add(client_online)
        session.commit()

    def unregister_client_online(self, client_id):
        session.query(DbClient).filter(DbClient.client_id == client_id).delete()

    def register_client_action(self, client_id, action, info):
        history = DbHistory(client_id, datetime.datetime.now(), action, info)
        session.add(history)
        session.commit()


if __name__ == '__main__':

    sto = ServerStorage()
    if not sto.get_client('kto1'):
        sto.add_client('kto1', 'cool')

    if not sto.get_client('kto1'):
        sto.add_client('kto1', 'cool')

    if not sto.get_client('kto'):
        sto.add_client('kto', 'admin')

    user_id1 = sto.get_client('kto1')
    sto.register_client_online(user_id1, '127.0.0.1')

    user_id2 = sto.get_client('kto')
    sto.register_client_online(user_id2, '127.0.0.1')

    sto.unregister_client_online()

    # history = DbHistory(client.id, datetime.datetime.now(), 'login', '127.0.0.1')
    # client_online = DbClientsOnline(client.id, '127.0.0.1')
    # session.add(history)
    # session.add(client_online)
    # session.commit()
    #
    # sto = ServerStorage()


