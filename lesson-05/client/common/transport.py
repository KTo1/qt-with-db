import sys
import socket
import threading

from PyQt5.QtCore import pyqtSignal, QObject


socket_lock = threading.Lock()


class Transport(threading.Thread, QObject):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, server_address, server_port, username):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.server_address = server_address
        self.server_port = server_port
        # self.database = database
        self.username = username
        self.transport = None

        # try:
        #     self.user_list_update()
        #     self.contacts_list_update()
        # except OSError as err:
        #     if err.errno:
        #         logger.critical(f'Потеряно соединение с сервером.')
        #         raise ServerError('Потеряно соединение с сервером!')
        #     logger.error('Timeout соединения при обновлении списков пользователей.')
        # except json.JSONDecodeError:
        #     logger.critical(f'Потеряно соединение с сервером.')
        #     raise ServerError('Потеряно соединение с сервером!')

        self.running = True

    def connect(self):
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            transport.connect((self.__server_address, self.__server_port))
        except ConnectionRefusedError as e:
            client_log.exception(str(e))
            sys.exit(1)

        message = self.create_presence(self.__user_name)
        send_message(transport, message)

        try:
            answer = self.process_answer(get_message(transport))
            print(f'{answer[RESPONSE]} : {answer[MESSAGE]}')

        except (ValueError, json.JSONDecodeError):
            client_log.exception('Не удалось декодировать сообщение сервера.')
            sys.exit(1)

    def run(self) -> None:
        pass
