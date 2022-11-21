from sqlalchemy import update, select
from datetime import datetime
from db_connect import session, engine
from db_contacts import DbContacts
from db_messages import DbMessages


DbContacts.metadata.create_all(engine)
DbMessages.metadata.create_all(engine)


class ClientStorage:

    def get_client(self, client_login):
        data = session.query(DbClient).filter(DbClient.login == client_login).limit(1).first()
        return data.id if data else 0

    def add_client(self, client, info=''):
        client = DbClient(client, info)
        session.add(client)
        session.commit()

    def update_client(self, client_id, info=''):
        u = update(DbClient)
        u = u.values({'info': info})
        u = u.where(DbClient.id == client_id)
        engine.execute(u)

    def register_client_online(self, client_id, ip_address, port, info):
        client_online = DbClientsOnline(client_id, ip_address, port, info)
        session.add(client_online)
        session.commit()

    def unregister_client_online(self, client_id):
        session.query(DbClientsOnline).filter(DbClientsOnline.client_id == client_id).delete()
        session.commit()

    def register_client_action(self, client_id, action, info):
        history = DbHistory(client_id, datetime.now(), action, info)
        session.add(history)
        session.commit()

    def get_clients_online(self):
        stm = select(DbClientsOnline.ip_address, DbClientsOnline.info, DbClient.login).join(DbClient, DbClientsOnline.client_id == DbClient.id, isouter=True)
        data = []
        result = session.execute(stm)

        for row in result:
            data.append(row)

        return data

    def get_register_clients(self):
        data = session.query(DbClient).all()
        return data

    def get_history(self, client_id):
        data = []
        if client_id:
            stm = select(DbClient.login, DbHistory).where(DbHistory.client_id == client_id).join(DbClient, DbHistory.client_id == DbClient.id, isouter=True)
        else:
            stm = select(DbClient.login, DbHistory).join(DbClient, DbHistory.client_id == DbClient.id, isouter=True)

        result = session.execute(stm)

        for row in result:
            data.append(row)

        return data

    def clear_contacts(self):
        session.query(DbContacts).delete()
        session.commit()

if __name__ == '__main__':

    sto = ClientStorage()
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

    sto.unregister_client_online(user_id1)
    sto.unregister_client_online(user_id2)

    sto.register_client_action(user_id1, 'login', '127.0.0.1')
    sto.register_client_action(user_id1, 'exit', '127.0.0.1')

    sto.register_client_action(user_id2, 'login', '127.0.0.1')
    sto.register_client_action(user_id2, 'exit', '127.0.0.1')

