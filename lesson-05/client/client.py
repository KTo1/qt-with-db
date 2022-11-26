import re
import dis
import sys
import json
import time
import socket
import threading

from PyQt5.QtWidgets import QApplication

from common.variables import (DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, PRESENCE, TIME, USER,
                              ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, EXIT, TO_USERNAME, USERS_ONLINE,
                              ACTION_GET_CONTACTS, ACTION_ADD_CONTACT, ACTION_DEL_CONTACT)
from common.utils import get_message, send_message, parse_cmd_parameter, PortField, result_from_stdout
from common.exceptions import CodeException
from common.transport import Transport
from logs.client_log_config import client_log
from logs.decorators import log
from db.client_storage import ClientStorage
from views.nickname import NicknameForm
from views.client_gui import ClientGui


class ClientVerifier(type):

    def __init__(self, *args, **kwargs):

        super(ClientVerifier, self).__init__(*args, **kwargs)

        for attr, val in args[2].items():
            if isinstance(val, socket.socket):
                raise CodeException('Сокеты в атрибутах запрещены.')

        re_tcp = r'.*LOAD_ATTR.*SOCK_STREAM.*'
        re_accept = r'.*LOAD_METHOD.*accept.*'
        re_listen = r'.*LOAD_METHOD.*listen.*'

        result_string = result_from_stdout(dis.dis, self)

        if not re.search(re_tcp, result_string):
            raise CodeException('Допустимы только TCP сокеты.')

        if re.search(re_accept, result_string):
            raise CodeException('Вызовы метода accept недопустимы.')

        if re.search(re_listen, result_string):
            raise CodeException('Вызовы метода listen недопустимы.')


class Client(metaclass=ClientVerifier):
    """
    Класс клиент
    """

    __server_port = PortField()

    def __init__(self, server_address, server_port, client_name):
        self.__server_address = server_address
        self.__server_port = server_port
        self.__client_name = client_name
        self.__storage = ClientStorage()
        self.__storage = ClientStorage()
        self.__transport = Transport(server_address, server_port, client_name)

# region protocol

    def create_common_message(self, account_name, action):
        result = {
            ACTION: action,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }

        return result

    def create_contacts_request(self, account_name):
        return self.create_common_message(account_name, ACTION_GET_CONTACTS)

    def create_add_contacts_message(self, account_name, contact_name):
        result = self.create_common_message(account_name, ACTION_ADD_CONTACT)
        result[TO_USERNAME] = contact_name

        return result

    def create_del_contacts_message(self, account_name, contact_name):
        result = self.create_common_message(account_name, ACTION_DEL_CONTACT)
        result[TO_USERNAME] = contact_name

        return result

    def create_online_request(self, account_name):
        """
        Функция генерирует запрос о пользователях онлайн
        :param account_name:
        :return:
        """

        return self.create_common_message(account_name, USERS_ONLINE)

    def create_presence(self, account_name):
        """
        Функция генерирует запрос о присутствии клиента
        :param account_name:
        :return:
        """

        return self.create_common_message(account_name, PRESENCE)

    def create_exit_message(self, account_name):
        """
        Функция генерирует запрос о выходе клиента
        :param account_name:
        :return:
        """

        return self.create_common_message(account_name, EXIT)

    def create_message(self, message, account_name, to_clientname):
        """
        Функция генерирует запрос о сообщении клиента
        :param message:
        :param account_name:
        :param to_clientname:
        :return:
        """

        result = self.create_common_message(account_name, MESSAGE)
        result[MESSAGE] = message
        result[TO_USERNAME] = to_clientname

        return result

# endregion

# region db

    def add_message(self, login_from, login_to, message):
        self.__storage.add_message(login_from, login_to, message)

    def get_messages(self):
        self.__storage.get_messages()

# endregion

    def process_answer(self, answer):
        """
        Функция разбирает ответ сервера
        :param answer:
        :return:
        """

        if not answer:
            return ''

        if RESPONSE in answer:
            if TIME in answer:
                answer[TIME] = time.strftime('%d.%m.%Y %H:%M', time.localtime(answer[TIME]))

            return answer

        raise ValueError

    def __print_help(self):
        """
        Выводит справку
        """

        help_string = 'Справка по командам:\n'
        help_string += '/help - эта справка\n'
        help_string += '/contacts - список контактов\n'
        help_string += '/contact add|del <contact> - добавление|удаление в|из список контактов\n'
        help_string += '/online - кто онлайн?\n'
        help_string += '/exit - выход\n'
        help_string += '/имя_пользователя сообщение - сообщение пользователю\n'

        print(help_string)

    def get_username_from_msg(self, command):
        """
        Извлекает имя пользователя из сообщений
        :param command:
        :return: Имя пользователя
        """
        if not command or not isinstance(command, str):
            return None

        # return command.split()[0].replace('/', '')
        # оставил с / чтобы удобно было копировать
        return command.split()[0]

    def send_messages(self, transport, client_name):
        """
        Для потока записи сообщений
        :param transport:
        :param client_name:
        :return:
        """

        while True:
            msg = input(f'<{client_name}> Введите непустое сообщение (/help - помощь): ')
            if not msg:
                continue

            if msg == '/exit' or msg == '.учше':
                send_message(transport, self.create_exit_message(client_name))
                print('Bye!')
                time.sleep(2)
                break

            if msg == '/help' or msg == '.рудз':
                self.__print_help()
                continue

            if msg == '/contacts' or msg == '.сщтефсеы':
                send_message(transport, self.create_contacts_request(client_name))
                continue

            if msg.startswith('/contact'):
                command = msg.split()[1]
                contact_name = msg.split()[2]
                if command == 'add':
                    send_message(transport, self.create_add_contacts_message(client_name, contact_name))
                else:
                    send_message(transport, self.create_del_contacts_message(client_name, contact_name))
                continue

            if msg == '/online' or msg == '.щтдшту':
                send_message(transport, self.create_online_request(client_name))
                continue

            to_clientname = self.get_username_from_msg(msg)

            if to_clientname and not to_clientname == client_name:
                message = msg.replace(to_clientname, '')
                self.add_message(client_name, to_clientname.replace('/', ''), message)
                send_message(transport, self.create_message(message, client_name, to_clientname))

    def recv_messages(self, transport):
        """
        Для потока чтения сообщений
        :param transport:
        :return:
        """

        while True:
            answer = self.process_answer(get_message(transport))
            if answer:
                print()
                print('Сообщение от сервера: ')
                print(f'<{answer[TIME]}> {answer[USER]}: {answer[MESSAGE]}')
                self.add_message(answer[USER], self.__client_name, answer[MESSAGE])

    def process_gui(self):
        client_app = QApplication(sys.argv)

        client_gui = ClientGui()
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
        self.__transport.setDaemon(True)
        self.__transport.start()

        self.process_gui()

        self.__transport.transport_shutdown()
        self.__transport.join()

        # sender = threading.Thread(target=self.send_messages, args=(transport, self.__user_name))
        # receiver = threading.Thread(target=self.recv_messages, args=(transport,))
        # gui = threading.Thread(target=self.process_gui)
        #
        # # sender.daemon = True
        # # receiver.daemon = True
        # gui.daemon = True
        #
        # # sender.start()
        # # receiver.start()
        # gui.start()
        #
        # while True:
        #     time.sleep(1)
        #     if receiver.is_alive() and gui.is_alive():
        #         continue
        #     break


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
