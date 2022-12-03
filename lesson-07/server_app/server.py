import os
import re
import dis
import sys
import json
import time
import socket
import threading
import configparser

from select import select
from datetime import datetime
from PyQt5.QtWidgets import QApplication

from server_app.common.variables import (MAX_CONNECTIONS, RESPONSE, ERROR, TIME, USER, ACTION, ACCOUNT_NAME, PRESENCE,
                                         MESSAGE, EXIT, TO_USERNAME, USERNAME_SERVER, USERS_ONLINE, ACTION_GET_CONTACTS,
                                         ACTION_ADD_CONTACT, ACTION_DEL_CONTACT, ACTION_GET_CLIENTS)
from server_app.common.utils import get_message, send_message, parse_cmd_parameter, PortField, result_from_stdout
from server_app.common.exceptions import CodeException
from server_app.common.decorators import login_required
from server_app.logs.server_log_config import server_log
from server_app.db.server_storage import ServerStorage
from server_app.views.server_gui import ServerGui


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

    def __init__(self, listen_address, listen_port, config_file_path):
        self.__clients_online_db = {}
        self.__listen_address = listen_address
        self.__listen_port = listen_port
        self.__storage = ServerStorage()
        self.__config_file_path = config_file_path
        self.__clients_sockets = []

# region protocol

    def process_client_message(self, message):
        """
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клиента, проверяет корректность,
        возвращает словарь-ответ для клиента
        """

        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            return {RESPONSE: 200, MESSAGE: message}

        if ACTION in message and message[ACTION] == MESSAGE and TIME in message and USER in message:
            return {RESPONSE: 201, MESSAGE: message}

        if ACTION in message and message[ACTION] == EXIT and TIME in message and USER in message:
            return {RESPONSE: 202, MESSAGE: message}

        if ACTION in message and message[ACTION] == USERS_ONLINE and TIME in message and USER in message:
            return {RESPONSE: 203, MESSAGE: message}

        if ACTION in message and message[ACTION] == ACTION_GET_CONTACTS and TIME in message and USER in message:
            return {RESPONSE: 204, MESSAGE: message}

        if ACTION in message and message[ACTION] == ACTION_ADD_CONTACT and TIME in message and USER in message:
            return {RESPONSE: 205, MESSAGE: message}

        if ACTION in message and message[ACTION] == ACTION_DEL_CONTACT and TIME in message and USER in message:
            return {RESPONSE: 206, MESSAGE: message}

        if ACTION in message and message[ACTION] == ACTION_GET_CLIENTS and TIME in message and USER in message:
            return {RESPONSE: 207, MESSAGE: message}

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

    def create_ok_answer(self):
        """
        Генерирует ответ на приветствие
        :return:
        """

        message = self.create_common_message(301, USERNAME_SERVER)
        message[MESSAGE] = 'OK'

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

    def create_no_register_client_answer(self):
        """
        Генерирует сообщение пользователь не зарегистрирован
        :param response:
        :return:
        """

        message = self.create_common_message(208, USERNAME_SERVER)
        message[MESSAGE] = 'Пользователь не зарегистрирован.'

        return message

    def create_invalid_pwd_client_answer(self):
        """
        Генерирует сообщение пароль не верный
        :param response:
        :return:
        """

        message = self.create_common_message(209, USERNAME_SERVER)
        message[MESSAGE] = 'Пароль не верный.'

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

    def create_get_clients_answer(self):
        clients = self.__storage.get_register_clients()
        message = self.create_common_message(207, USERNAME_SERVER)
        message[MESSAGE] = clients

        return message

    def create_client_contacts_answer(self, client_name):
        """
        Генерирует сообщение пользователи онлайн
        :param response:
        :return:
        """

        message = self.create_common_message(203, USERNAME_SERVER)

        client_id = self.__storage.get_client_id(client_name)
        contacts = self.__storage.get_contacts(client_id)

        message[MESSAGE] = contacts

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

    def create_add_contact_answer(self):
        message = self.create_common_message(300, USERNAME_SERVER)
        message[MESSAGE] = 'Ok.'

        return message

    def create_del_contact_answer(self):
        message = self.create_common_message(300, USERNAME_SERVER)
        message[MESSAGE] = 'Ok.'

        return message

# endregion

# region db

    def get_clients_online(self):
        clients_online = self.__storage.get_clients_online()
        result = 'Список пользователей онлайн: \n'
        for elem in clients_online:
            result += f'login: {str(elem[2])}, ip: {elem[0]}, info: {elem[1]}' + '\n'
        return result

    def add_client_contact(self, client, contact):
        # TODO закешировать
        client_id = self.__storage.get_client_id(client)
        contact_id = self.__storage.get_client_id(contact)

        self.__storage.add_contact(client_id, contact_id)

        return True

    def del_client_contact(self, client, contact):
        # TODO закешировать
        client_id = self.__storage.get_client_id(client)
        contact_id = self.__storage.get_client_id(contact)

        self.__storage.del_contact(client_id, contact_id)

    def get_history(self, client):
        # TODO закешировать
        client_id = self.__storage.get_client_id(client)

        history = self.__storage.get_history(client_id)
        result = 'История: \n'
        for elem in history:
            result += str(elem) + '\n'
        return result

    def clear_online(self):
        self.__storage.clear_online()

    def register_client_online(self, client, socket, ip_address, port):
        # TODO закешировать
        client_id = self.__storage.get_client_id(client)

        self.__clients_online_db[client] = socket
        self.__storage.register_client_online(client_id, ip_address, port, datetime.now())

    def update_stat(self, sender, recipient):
        # TODO закешировать
        sender_id = self.__storage.get_client_id(sender)
        recipient_id = self.__storage.get_client_id(recipient)

        self.__storage.update_stat(sender_id, recipient_id)

    def register_client_action(self, client, action, info):
        # TODO закешировать
        client_id = self.__storage.get_client_id(client)

        self.__storage.register_client_action(client_id, action, info)

    def unregister_client_online(self, client):
        # TODO закешировать
        client_id = self.__storage.get_client_id(client)

        self.__storage.unregister_client_online(client_id)
        del self.__clients_online_db[client]

    def get_socket_on_clientname(self, to_client):
        return self.__clients_online_db.get(to_client.replace('/', ''))

# endregion

    def autorize(self, client_name, socket):

        client_message = get_message(socket)

        client = self.__storage.get_client(client_name)

        if not client:
            try:
                send_message(socket, self.create_no_register_client_answer())
            except OSError:
                pass

            time.sleep(1)
            self.__clients_sockets.remove(socket)
            socket.close()

        if client:
            pwd_hash = client_message[MESSAGE].encode('ascii')
            if not client.pwd_hash == pwd_hash:
                try:
                    send_message(socket, self.create_invalid_pwd_client_answer())
                except OSError:
                    pass

                time.sleep(1)
                self.__clients_sockets.remove(socket)
                socket.close()

        send_message(socket, self.create_ok_answer())

    @login_required
    def __process_clients_messages(self, transport, response, client_address, client_socket, cl_sock_read, cl_sock_write, message_pool):

        # Пока так, 200 это приветствие
        if response[RESPONSE] == 200 and client_socket in cl_sock_write:
            transport.settimeout(10)
            client_name = response[MESSAGE][USER][ACCOUNT_NAME]
            send_message(client_socket, response)
            self.autorize(client_name, client_socket)
            transport.settimeout(1)

            self.register_client_online(client_name, client_socket, client_address[0], client_address[1])

        # Пока так, 201 это сообщение
        if response[RESPONSE] == 201:
            client_socket = self.get_socket_on_clientname(response[MESSAGE][TO_USERNAME])

            if client_socket:
                message_pool.append((client_socket, self.create_answer(response)))
            else:
                message_pool.append((client_socket, self.create_no_client_answer()))

            sender_name = response[MESSAGE][USER][ACCOUNT_NAME]
            recipient_name = response[MESSAGE][TO_USERNAME].replace('/', '')

            self.update_stat(sender_name, recipient_name)
            self.register_client_action(sender_name, 'send message', recipient_name)

        # Пока так, 202 это выход
        if response[RESPONSE] == 202 and client_socket in cl_sock_write:
            self.__clients_sockets.remove(client_socket)
            client_socket.close()

            self.register_client_action(response[MESSAGE][USER][ACCOUNT_NAME], 'exit', str(client_address))
            self.unregister_client_online(response[MESSAGE][USER][ACCOUNT_NAME])

        # Пока так, 203 это запрос пользователей онлайн
        if response[RESPONSE] == 203 and client_socket in cl_sock_write:
            self.register_client_action(response[MESSAGE][USER][ACCOUNT_NAME], 'get online', str(client_address))
            message_pool.append((client_socket, self.create_client_online_answer()))

        # Пока так, 204 это запрос списка контактов
        if response[RESPONSE] == 204 and client_socket in cl_sock_write:
            client_name = response[MESSAGE][USER][ACCOUNT_NAME]
            self.register_client_action(client_name, 'get contacts', str(client_address))
            message_pool.append((client_socket, self.create_client_contacts_answer(client_name)))

        # Пока так, 205 это запрос на добавление в контакты
        if response[RESPONSE] == 205 and client_socket in cl_sock_write:
            client_name = response[MESSAGE][USER][ACCOUNT_NAME]
            contacts_name = response[MESSAGE][TO_USERNAME]

            self.add_client_contact(client_name, contacts_name)

            self.register_client_action(client_name, 'add contact', str(client_address))
            message_pool.append((client_socket, self.create_add_contact_answer()))

        # Пока так, 206 это запрос на удаление из контактов
        if response[RESPONSE] == 206 and client_socket in cl_sock_write:
            client_name = response[MESSAGE][USER][ACCOUNT_NAME]
            contacts_name = response[MESSAGE][TO_USERNAME]

            self.del_client_contact(client_name, contacts_name)

            self.register_client_action(client_name, 'del contact', str(client_address))
            message_pool.append((client_socket, self.create_del_contact_answer()))

        # Пока так, 207 это запрос на список клиентов
        if response[RESPONSE] == 207 and client_socket in cl_sock_write:
            client_name = response[MESSAGE][USER][ACCOUNT_NAME]
            self.register_client_action(client_name, 'get clients', str(client_address))
            message_pool.append((client_socket, self.create_get_clients_answer()))

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

        self.__clients_sockets = []
        server_log.info(f'Сервер запущен по адресу: {self.__listen_address}: {self.__listen_port}')

        while True:
            try:
                client_sock, client_address = transport.accept()
            except OSError as e:
                pass
            else:
                self.__clients_sockets.append(client_sock)
            finally:
                wait = 0
                message_pool = []

                for client_socket in self.__clients_sockets:
                    # На мой взгляд логичнее это вынести за цикл, но на виндовс так не работает
                    cl_sock_read, cl_sock_write = [], []
                    cl_sock_read, cl_sock_write, _ = select(self.__clients_sockets, self.__clients_sockets, [], wait)
                    try:
                        if client_socket in cl_sock_read:
                            client_message = get_message(client_socket)
                            response = self.process_client_message(client_message)

                            self.__process_clients_messages(transport, response, client_address, client_socket, cl_sock_read, cl_sock_write, message_pool)

                    except ConnectionResetError as e:
                        server_log.exception(f'Произошла ошибка: {str(e)}')
                        self.__clients_sockets.remove(client_socket)
                        client_socket.close()

                    except (ValueError, json.JSONDecodeError, TypeError):
                        server_log.exception('Принято некорректное сообщение от клиента')
                        self.__clients_sockets.remove(client_socket)
                        client_socket.close()

                for message in message_pool:
                    _, cl_sock_write, _ = select([], self.__clients_sockets, [], wait)

                    client_socket = message[0]
                    message_send = message[1]

                    if client_socket in cl_sock_write:
                        send_message(client_socket, message_send)

    def __process_gui(self):
        """
        Для потока администрирования
        :return:
        """

        server_app = QApplication(sys.argv)

        server_gui = ServerGui(self.__config_file_path)
        server_gui.set_timer(3000)
        server_gui.show()

        server_gui.status_message('Welcome, admin. SHODAN is waiting you.')

        server_app.exec()

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

    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.relpath(__file__))
    config_file_path = os.path.join(dir_path, 'settings.ini')
    config.read(config_file_path)

    listen_address = parse_cmd_parameter('-a', sys.argv, config['SETTINGS']['default_address'],
                                         'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
    listen_port = parse_cmd_parameter('-p', sys.argv, config['SETTINGS']['default_port'],
                                      'После параметра -\'p\' необходимо указать номер порта.')

    listen_port = int(listen_port)

    if listen_port is None or listen_address is None:
        raise ValueError('Неверно заданы параметры командной строки')

    server = Server(listen_address, int(listen_port), config_file_path)
    server.run()
