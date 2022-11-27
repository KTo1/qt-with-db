from sqlalchemy import or_

from db_connect import session, engine
from db_messages import DbMessages

DbMessages.metadata.create_all(engine)


class ClientStorage:

    def add_message(self, date_action, login_from, login_to, message):
        message = DbMessages(date_action, login_from, login_to, message)
        session.add(message)
        session.commit()

    def del_message(self):
        pass

    def get_messages(self, contact, limit):
        data = []

        if limit:
            stm = session.query(DbMessages).filter(
                or_(DbMessages.login_from == contact, DbMessages.login_to == contact)).order_by(
                DbMessages.date_action).limit(limit).all()
        else:
            stm = session.query(DbMessages).filter(
                or_(DbMessages.login_from == contact, DbMessages.login_to == contact)).order_by(
                DbMessages.date_action).all()

        for row in stm:
            data.append(row)

        return data


if __name__ == '__main__':
    pass
