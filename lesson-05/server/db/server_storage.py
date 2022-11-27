from sqlalchemy import update, select, and_
from datetime import datetime
from db_connect import session, engine
from db_client import DbClient
from db_history import DbHistory
from db_clients_online import DbClientsOnline
from db_contacts import DbContacts
from db_stat import DbStat


DbClient.metadata.create_all(engine)
DbHistory.metadata.create_all(engine)
DbClientsOnline.metadata.create_all(engine)
DbContacts.metadata.create_all(engine)
DbStat.metadata.create_all(engine)


class ServerStorage:

    def get_client(self, client_login):
        data = session.query(DbClient).filter(DbClient.login == client_login).limit(1).first()
        return data.id if data else 0

    def add_client(self, client, info=''):
        client = DbClient(client, info)
        session.add(client)
        session.commit()

    def update_client(self, client_id, info=''):
        upd = update(DbClient)
        upd = upd.values({'info': info})
        upd = upd.where(DbClient.id == client_id)
        engine.execute(upd)

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
        stm = select(DbClientsOnline.ip_address, DbClientsOnline.port, DbClientsOnline.info, DbClient.login).join(DbClient,
                                                                                            DbClientsOnline.client_id == DbClient.id,
                                                                                            isouter=True)
        data = []
        result = session.execute(stm)

        for row in result:
            data.append(row)

        return data

    def get_register_clients(self):
        data = []
        stm = session.query(DbClient.login).all()
        for row in stm:
            data.append(row.login)
        return data

    def get_history(self, client_id):
        data = []
        if client_id:
            stm = select(DbClient.login).where(DbHistory.client_id == client_id).join(DbClient,
                                                                                      DbHistory.client_id == DbClient.id,
                                                                                      isouter=True)
        else:
            stm = select(DbClient.login).join(DbClient, DbHistory.client_id == DbClient.id, isouter=True)

        result = session.execute(stm)

        for row in result:
            data.append(row)

        return data

    def update_stat(self, sender_id, recipient_id):
        sender_row = session.query(DbStat).filter(DbStat.client_id == sender_id).limit(1).first()
        recipient_row = session.query(DbStat).filter(DbStat.client_id == recipient_id).limit(1).first()

        if sender_row:
            sender_row.sent += 1
        else:
            sender = DbStat(sender_id)
            sender.sent, sender.recv = 1, 0
            session.add(sender)

        if recipient_row:
            recipient_row.recv += 1
        else:
            recipient = DbStat(recipient_id)
            recipient.sent, recipient.recv = 0, 1
            session.add(recipient)

        session.commit()

    def get_stat(self):
        data = []
        stm = select(DbClient.login, DbClient.info, DbStat.sent, DbStat.recv).join(DbClient, DbStat.client_id == DbClient.id, isouter=True)

        result = session.execute(stm)

        for row in result:
            data.append(row)

        return data

    def clear_online(self):
        session.query(DbClientsOnline).delete()
        session.commit()

    def add_contact(self, client_id, contact_id):
        exist = session.query(DbContacts).filter(
            and_(DbContacts.client_id == client_id, DbContacts.contact_id == contact_id)).limit(1).first()
        if not exist:
            contact = DbContacts(client_id, contact_id)
            session.add(contact)
            session.commit()

    def del_contact(self, client_id, contact_id):
        exist = session.query(DbContacts).filter(DbContacts.client_id == client_id).limit(1).first()
        if exist:
            session.query(DbContacts).where(
                and_(DbContacts.client_id == client_id, DbContacts.contact_id == contact_id)).delete()
            session.commit()

    def get_contacts(self, client_id):
        data = []
        stm = select(DbClient.login, DbContacts).where(DbContacts.client_id == client_id).join(DbClient,
                                                                                               DbContacts.contact_id == DbClient.id,
                                                                                               isouter=True)

        result = session.execute(stm)

        for row in result:
            data.append(row.login)

        return data


if __name__ == '__main__':

    sto = ServerStorage()
    if not sto.get_client('kto1'):
        sto.add_client('kto1', 'cool')

    if not sto.get_client('kto1'):
        sto.add_client('kto1', 'cool')

    if not sto.get_client('kto'):
        sto.add_client('kto', 'admin')

    client_id1 = sto.get_client('kto1')
    sto.register_client_online(client_id1, '127.0.0.1', '1111', '')

    client_id2 = sto.get_client('kto')
    sto.register_client_online(client_id2, '127.0.0.1', '1111', '')

    sto.unregister_client_online(client_id1)
    sto.unregister_client_online(client_id2)

    sto.register_client_action(client_id1, 'login', '127.0.0.1')
    sto.register_client_action(client_id1, 'exit', '127.0.0.1')

    sto.register_client_action(client_id2, 'login', '127.0.0.1')
    sto.register_client_action(client_id2, 'exit', '127.0.0.1')

    sto.add_contact(client_id1, client_id1)
    sto.add_contact(client_id1, client_id1)
    sto.add_contact(client_id1, client_id2)

    sto.add_contact(client_id2, client_id2)
    sto.add_contact(client_id2, client_id2)
    sto.add_contact(client_id2, client_id1)

    sto.del_contact(client_id1, client_id1)
    sto.del_contact(client_id2, client_id2)

    print(sto.get_contacts(1))
