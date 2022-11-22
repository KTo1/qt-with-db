from db_connect import session, engine
from db_messages import DbMessages

DbMessages.metadata.create_all(engine)


class ClientStorage:

    def add_message(self, login_from, login_to, message):
        message = DbMessages(login_from, login_to, message)
        session.add(message)
        session.commit()

    def del_message(self):
        pass

    def get_messages(self):
        data = session.query(DbMessages).all()
        return data


if __name__ == '__main__':
    pass


