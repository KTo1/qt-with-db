import sys
import time

from PyQt5.QtWidgets import QApplication

from common.variables import (DEFAULT_PORT, DEFAULT_IP_ADDRESS)
from common.utils import parse_cmd_parameter, PortField
from common.transport import Transport
from logs.client_log_config import client_log
from db.client_storage import ClientStorage
from views.nickname import NicknameForm
from views.client_gui import ClientGui


class Client():
    """
    Класс клиент
    """

    __server_port = PortField()

    def __init__(self, server_address, server_port, client_name):
        self.__server_address = server_address
        self.__server_port = server_port
        self.__client_name = client_name

        self.__storage = ClientStorage()

        self.__transport = Transport(server_address, server_port, client_name)
        self.__transport.set_logger(client_log)
        self.__transport.set_storage(ClientStorage())

    # def recv_messages(self, transport):
    #     """
    #     Для потока чтения сообщений
    #     :param transport:
    #     :return:
    #     """
    #
    #     while True:
    #         answer = self.process_answer(get_message(transport))
    #         if answer:
    #             print()
    #             print('Сообщение от сервера: ')
    #             print(f'<{answer[TIME]}> {answer[USER]}: {answer[MESSAGE]}')
    #             self.add_message(answer[USER], self.__client_name, answer[MESSAGE])

    def process_gui(self):
        client_app = QApplication(sys.argv)

        client_gui = ClientGui(self.__transport, self.__storage)
        client_gui.show()
        client_gui.status_message('Welcome, admin. SHODAN is waiting you.')

        client_app.exec_()

    def run(self):
        """
        Запускает клиент.
        -u User - имя пользователя
        Пример: client.py -u Guest -p 8888 -a 127.0.0.1
        Пример: client.py -u Guest -p 8888 -a 127.0.0.1
        """

        self.__transport.connect()
        self.__transport.daemon = True
        self.__transport.start()

        self.process_gui()

        time.sleep(2)

        self.__transport.shutdown()
        self.__transport.join()


if __name__ == '__main__':

    server_address = parse_cmd_parameter('-a', sys.argv, DEFAULT_IP_ADDRESS,
                                         'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
    server_port = parse_cmd_parameter('-p', sys.argv, DEFAULT_PORT,
                                      'После параметра -\'p\' необходимо указать номер порта.')
    client_name = parse_cmd_parameter('-u', sys.argv, '',
                                    'После параметра -\'u\' необходимо указать имя пользователя.')

    if server_port is None or server_address is None or client_name is None:
        raise ValueError('Неверно заданы параметры командной строки')

    # process parameter
    server_port = int(server_port)

    # Создаём клиентское приложение
    client_app = QApplication(sys.argv)

    # Если имя пользователя не было указано в командной строке то запросим его
    if not client_name:
        start_dialog = NicknameForm()
        start_dialog.show()
        client_app.exec_()

        # Если пользователь ввёл имя и нажал ОК, то сохраняем ведённое и удаляем объект, инааче выходим
        if start_dialog.ok_pressed:
            client_name = start_dialog.lineEdit_nickname.text()
            del start_dialog
        else:
            exit(0)

    client = Client(server_address, server_port, client_name)
    client.run()
