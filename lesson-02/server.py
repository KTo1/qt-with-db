import sys
import json
import time
import socket

from select import select

from common.variables import (MAX_CONNECTIONS, RESPONSE, ERROR, TIME, USER, ACTION, ACCOUNT_NAME, PRESENCE,
                              DEFAULT_PORT, DEFAULT_IP_ADDRESS, MESSAGE, EXIT, TO_USERNAME, USERNAME_SERVER,
                              USERS_ONLINE)
from common.utils import get_message, send_message, parse_cmd_parameter, PortField
from logs.server_log_config import server_log
from logs.decorators import log


class Server:
    """
    Класс сервер
    """

    __listen_port = PortField()

    def __init__(self, listen_address, listen_port):
        self.__users_db = ['Guest', 'Bazil', 'KTo', 'User']
        self.__users_online_db = {}
        self.__listen_address = listen_address
        self.__listen_port = listen_port

    def process_client_message(self, message):
        """
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клиента, проверяет корректность,
        возвращает словарь-ответ для клиента
        """

        server_log.debug(f'Вызов функции "process_client_message", с параметрами: {str(message)}')

        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] in self.__users_db:
            return {RESPONSE: 200, MESSAGE: message}

        if ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] in self.__users_db:
            return {RESPONSE: 201, MESSAGE: message}

        if ACTION in message and message[ACTION] == EXIT and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] in self.__users_db:
            return {RESPONSE: 202, MESSAGE: message}

        if ACTION in message and message[ACTION] == USERS_ONLINE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] in self.__users_db:
            return {RESPONSE: 203, MESSAGE: message}

        return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    def create_common_message(self, response, user):
        return {
            RESPONSE: response,
            TIME: time.time(),
            USER: user,
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

    def create_no_user_answer(self):
        """
        Генерирует сообщение пользователь не найден
        :param response:
        :return:
        """

        message = self.create_common_message(201, USERNAME_SERVER)
        message[MESSAGE] = 'Пользователь не найден, возможно он не в сети, или вы ошиблись в имени.'

        return message

    def create_user_online_answer(self):
        """
        Генерирует сообщение пользователи онлайн
        :param response:
        :return:
        """

        message = self.create_common_message(203, USERNAME_SERVER)

        message_text = 'Список пользователей онлайн: \n'
        message_text += '\n'.join(['/' + user for user in self.__users_online_db])

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

    def register_user_online(self, user, socket):
        self.__users_online_db[user] = socket

    def unregister_user_online(self, user):
        del self.__users_online_db[user]

    def get_socket_on_username(self, to_username):
        return self.__users_online_db.get(to_username.replace('/', ''))

    def run(self):
        """
        Запускает сервер.
        Пример: server.py -p 8888 -a 127.0.0.1
        """

        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        transport.bind((self.__listen_address, self.__listen_port))

        transport.listen(MAX_CONNECTIONS)
        transport.settimeout(1)

        clients_sockets = []
        server_log.info(f'Сервер запущен по адресу: {self.__listen_address}: {self.__listen_port}')

        while True:
            try:
                client_sock, client_address = transport.accept()
            except OSError as e:
                print(str(e))
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
                                self.register_user_online(response[MESSAGE][USER][ACCOUNT_NAME], client_socket)

                            # Пока так, 201 это сообщение
                            if response[RESPONSE] == 201:
                                user_socket = self.get_socket_on_username(response[MESSAGE][TO_USERNAME])
                                if user_socket:
                                    message_pool.append((user_socket, self.create_answer(response)))
                                else:
                                    message_pool.append((client_socket, self.create_no_user_answer()))

                            # Пока так, 202 это выход
                            if response[RESPONSE] == 202 and client_socket in cl_sock_write:
                                clients_sockets.remove(client_socket)
                                client_socket.close()
                                self.unregister_user_online(response[MESSAGE][USER][ACCOUNT_NAME])

                            # Пока так, 203 это запрос пользователей онлайн
                            if response[RESPONSE] == 203 and client_socket in cl_sock_write:
                                message_pool.append((client_socket, self.create_user_online_answer()))

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


if __name__ == '__main__':
    listen_address = parse_cmd_parameter('-a', sys.argv, DEFAULT_IP_ADDRESS,
                                         'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
    listen_port = parse_cmd_parameter('-p', sys.argv, DEFAULT_PORT,
                                      'После параметра -\'p\' необходимо указать номер порта.')

    if listen_port is None or listen_address is None:
        raise ValueError('Неверно заданы параметры командной строки')

    # process parameter
    listen_port = int(listen_port)

    server = Server(listen_address, listen_port)
    server.run()
