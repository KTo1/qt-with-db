import re
import dis
import sys
import json
import time
import socket
import threading
from datetime import datetime

from select import select

from common.variables import (MAX_CONNECTIONS, RESPONSE, ERROR, TIME, USER, ACTION, ACCOUNT_NAME, PRESENCE,
                              DEFAULT_PORT, DEFAULT_IP_ADDRESS, MESSAGE, EXIT, TO_USERNAME, USERNAME_SERVER,
                              USERS_ONLINE)
from common.utils import get_message, send_message, parse_cmd_parameter, PortField, result_from_stdout
from common.exceptions import CodeException
from logs.server_log_config import server_log
from logs.decorators import log
from db.server_storage import ServerStorage


class ServerVerifier(type):

    def __init__(self, *args, **kwargs):

        super(ServerVerifier, self).__init__(*args, **kwargs)

        re_tcp = r'.*LOAD_ATTR.*SOCK_STREAM.*'
        re_connect = r'.*LOAD_METHOD.*connect.*'

        result_string = result_from_stdout(dis.dis, self)

        if not re.search(re_tcp, result_string):
            raise CodeException('Допустимы только TCP сокеты.')

        if re.search(re_connect, result_string):
            raise CodeException('Вызовы метода connect недопустимы.')


class Server(metaclass=ServerVerifier):
    """
    Класс сервер
    """

    __listen_port = PortField()

    def __init__(self, listen_address, listen_port):
        self.__clients_db = ['Guest', 'Bazil', 'KTo', 'User']
        self.__clients_online_db = {}
        self.__listen_address = listen_address
        self.__listen_port = listen_port
        self.__storage = ServerStorage()

    def process_client_message(self, message):
        """
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клиента, проверяет корректность,
        возвращает словарь-ответ для клиента
        """

        server_log.debug(f'Вызов функции "process_client_message", с параметрами: {str(message)}')

        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] in self.__clients_db:
            return {RESPONSE: 200, MESSAGE: message}

        if ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] in self.__clients_db:
            return {RESPONSE: 201, MESSAGE: message}

        if ACTION in message and message[ACTION] == EXIT and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] in self.__clients_db:
            return {RESPONSE: 202, MESSAGE: message}

        if ACTION in message and message[ACTION] == USERS_ONLINE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] in self.__clients_db:
            return {RESPONSE: 203, MESSAGE: message}

        return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    def create_common_message(self, response, client):
        return {
            RESPONSE: response,
            TIME: time.time(),
            USER: client,
            MESSAGE: ''
        }

    def create_presence_answer(self, response):
        """
        Генерирует ответ на приветствие
        :param response:
        :return:
        """

        message = self.create_common_message(200, response[MESSAGE][USER][ACCOUNT_NAME])
        message[MESSAGE] = 'enter, and say hi all!'

        return message

    def create_no_client_answer(self):
        """
        Генерирует сообщение пользователь не найден
        :param response:
        :return:
        """

        message = self.create_common_message(201, USERNAME_SERVER)
        message[MESSAGE] = 'Пользователь не найден, возможно он не в сети, или вы ошиблись в имени.'

        return message

    def create_client_online_answer(self):
        """
        Генерирует сообщение пользователи онлайн
        :param response:
        :return:
        """

        message = self.create_common_message(203, USERNAME_SERVER)

        message_text = 'Список пользователей онлайн: \n'
        message_text += '\n'.join(['/' + client for client in self.__clients_online_db])

        message[MESSAGE] = message_text

        return message

    def create_answer(self, response):
        """
        Генерирует сообщение пользователю
        :param response:
        :return:
        """

        message = self.create_common_message(201, response[MESSAGE][USER][ACCOUNT_NAME])
        message[MESSAGE] = response[MESSAGE][MESSAGE]

        return message

    def create_exit_answer(self, response):
        """
        Генерирует сообщение выхода
        :param response:
        :return:
        """

        message = self.create_common_message(202, response[MESSAGE][USER][ACCOUNT_NAME])
        message[MESSAGE] = 'exit and say by!'

        return message

    def get_clients_online(self):
        clients_online = self.__storage.get_clients_online()
        result = 'Список пользователей онлайн: \n'
        for elem in clients_online:
            result += f'login: {str(elem[2])}, ip: {elem[0]}, info: {elem[1]}' + '\n'
        return result

    def get_register_clients(self):
        clients = self.__storage.get_register_clients()
        result = 'Список зарегистрированных пользователей: \n'
        for elem in clients:
            result += str(elem) + '\n'
        return result

    def get_history(self, client):
        # TODO закешировать
        client_id = self.__storage.get_client(client)

        history = self.__storage.get_history(client_id)
        result = 'История: \n'
        for elem in history:
            result += str(elem) + '\n'
        return result

    def clear_online(self):
        self.__storage.clear_online()

    def register_client(self, client):
        client_id = self.__storage.get_client(client)
        if not client_id:
            self.__storage.add_client(client, datetime.now())
        else:
            self.__storage.update_client(client_id, datetime.now())

    def register_client_online(self, client, socket, ip_address, port):
        # TODO закешировать
        client_id = self.__storage.get_client(client)

        self.__clients_online_db[client] = socket
        self.__storage.register_client_online(client_id, ip_address, port, datetime.now())

    def register_client_action(self, client, action, info):
        # TODO закешировать
        client_id = self.__storage.get_client(client)

        self.__storage.register_client_action(client_id, action, info)

    def unregister_client_online(self, client):
        # TODO закешировать
        client_id = self.__storage.get_client(client)

        self.__storage.unregister_client_online(client_id)
        del self.__clients_online_db[client]

    def get_socket_on_clientname(self, to_client):
        return self.__clients_online_db.get(to_client.replace('/', ''))

    def __print_help(self):
        """
        Выводит справку
        """

        help_string = 'Справка по командам:\n'
        help_string += '/help - эта справка\n'
        help_string += '/online - кто онлайн?\n'
        help_string += '/clients - список пользователей сервера\n'
        help_string += '/hist client - история работы пользователя client, если пусто то все пользователи\n'
        help_string += '/stop - остановка сервера\n'

        print(help_string)

    def __process_messages(self):
        """
        Для потока обработки сообщений
        :return:
        """

        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        transport.bind((self.__listen_address, self.__listen_port))

        transport.listen(MAX_CONNECTIONS)
        transport.settimeout(1)

        self.clear_online()

        clients_sockets = []
        server_log.info(f'Сервер запущен по адресу: {self.__listen_address}: {self.__listen_port}')

        while True:
            try:
                client_sock, client_address = transport.accept()
            except OSError as e:
                pass
            else:
                clients_sockets.append(client_sock)
            finally:
                wait = 0
                message_pool = []

                for client_socket in clients_sockets:
                    # На мой взгляд логичнее это вынести за цикл, но на виндовс так не работает
                    cl_sock_read, cl_sock_write = [], []
                    cl_sock_read, cl_sock_write, _ = select(clients_sockets, clients_sockets, [], wait)
                    try:
                        if client_socket in cl_sock_read:
                            client_message = get_message(client_socket)
                            print(client_message)
                            response = self.process_client_message(client_message)

                            # Пока так, 200 это приветствие
                            if response[RESPONSE] == 200 and client_socket in cl_sock_write:
                                send_message(client_socket, response)
                                client_name = response[MESSAGE][USER][ACCOUNT_NAME]

                                self.register_client(client_name)
                                self.register_client_online(client_name, client_socket, str(client_address[0]), str(client_address[1]))
                                self.register_client_action(client_name, 'login', str(client_address))

                            # Пока так, 201 это сообщение
                            if response[RESPONSE] == 201:
                                client_socket = self.get_socket_on_clientname(response[MESSAGE][TO_USERNAME])

                                if client_socket:
                                    message_pool.append((client_socket, self.create_answer(response)))
                                else:
                                    message_pool.append((client_socket, self.create_no_client_answer()))

                                self.register_client_action(response[MESSAGE][USER][ACCOUNT_NAME], 'send message', response[MESSAGE][TO_USERNAME])

                            # Пока так, 202 это выход
                            if response[RESPONSE] == 202 and client_socket in cl_sock_write:
                                clients_sockets.remove(client_socket)
                                client_socket.close()

                                self.register_client_action(response[MESSAGE][USER][ACCOUNT_NAME], 'exit', str(client_address))
                                self.unregister_client_online(response[MESSAGE][USER][ACCOUNT_NAME])

                            # Пока так, 203 это запрос пользователей онлайн
                            if response[RESPONSE] == 203 and client_socket in cl_sock_write:
                                self.register_client_action(response[MESSAGE][USER][ACCOUNT_NAME], 'get online', str(client_address))
                                message_pool.append((client_socket, self.create_client_online_answer()))

                    except (ValueError, json.JSONDecodeError):
                        server_log.exception('Принято некорректное сообщение от клиента')
                        clients_sockets.remove(client_socket)
                        client_socket.close()

                for message in message_pool:
                    _, cl_sock_write, _ = select([], clients_sockets, [], wait)

                    client_socket = message[0]
                    message_send = message[1]

                    if client_socket in cl_sock_write:
                        send_message(client_socket, message_send)

    def __process_gui(self):
        """
        Для потока администрирования
        :return:
        """

        print('Welcome, admin. SHODAN is waiting you.')

        while True:
            msg = input(f'Введите команду (/help - помощь): ')
            if not msg:
                continue

            if msg == '/stop' or msg == '.ыещз':
                print('Bye!')
                time.sleep(2)
                break

            if msg == '/online' or msg == '.ыещз':
                print(self.get_clients_online())

            if msg == '/clients' or msg == '.ыещз':
                print(self.get_register_clients())

            if '/hist' in msg:
                param = msg.split()
                client_name = param[1] if len(param) > 1 else ''
                print(self.get_history(client_name))

            if msg == '/help' or msg == '.рудз':
                self.__print_help()

    def run(self):
        """
        Запускает сервер.
        Пример: server.py -p 8888 -a 127.0.0.1
        """

        process_messages = threading.Thread(target=self.__process_messages, daemon=True)
        process_gui = threading.Thread(target=self.__process_gui, daemon=True)

        process_messages.daemon = True
        process_gui.daemon = True

        process_messages.start()
        process_gui.start()

        while True:
            time.sleep(1)
            if process_messages.is_alive() and process_gui.is_alive():
                continue
            break


if __name__ == '__main__':
    listen_address = parse_cmd_parameter('-a', sys.argv, DEFAULT_IP_ADDRESS,
                                         'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
    listen_port = parse_cmd_parameter('-p', sys.argv, DEFAULT_PORT,
                                      'После параметра -\'p\' необходимо указать номер порта.')

    if listen_port is None or listen_address is None:
        raise ValueError('Неверно заданы параметры командной строки')

    server = Server(listen_address, int(listen_port))
    server.run()
