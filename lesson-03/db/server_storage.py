from db_connect import session, engine
from db_client import DbClient
from db_history import DbHistory


DbClient.metadata.create_all(engine)
DbHistory.metadata.create_all(engine)


class ServerStorage:
    pass


if __name__ == '__main__':
    client = DbClient('kto', 'admin')

    session.add(client)
    session.commit()


