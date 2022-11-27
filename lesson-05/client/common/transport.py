import sys
import json
import time
import socket
import threading

from PyQt5.QtCore import pyqtSignal, QObject
from .utils import send_message, get_message
from .variables import (TIME, USER, RESPONSE, MESSAGE, ACTION, ACCOUNT_NAME, ACTION_GET_CONTACTS, ACTION_ADD_CONTACT,
                        TO_USERNAME, ACTION_DEL_CONTACT, USERS_ONLINE, PRESENCE, EXIT, ACTION_GET_CLIENTS)


socket_lock = threading.Lock()


class Transport(threading.Thread, QObject):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, server_address, server_port, client_name):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.__server_address = server_address
        self.__server_port = server_port
        self.__client_name = client_name
        self.__storage = None
        self.__logger = None
        self.__transport = None

        self.running = True

    def set_logger(self, logger):
        self.__logger = logger

    def set_storage(self, storage):
        self.__storage = storage

    def shutdown(self):
        self.__logger.info('Отключение.')

    def connect(self):
        self.__transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.__transport.connect((self.__server_address, self.__server_port))
        except ConnectionRefusedError as e:
            self.__logger.exception(str(e))
            sys.exit(1)

        message = self.create_presence(self.__client_name)
        send_message(self.__transport, message)

        try:
            answer = self.process_answer(get_message(self.__transport))
            print(f'{answer[RESPONSE]} : {answer[MESSAGE]}')

        except (ValueError, json.JSONDecodeError):
            self.__logger.exception('Не удалось декодировать сообщение сервера.')
            sys.exit(1)

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

    def create_clients_request(self, account_name):
        return self.create_common_message(account_name, ACTION_GET_CLIENTS)

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

# endregion

    def get_contacts_list(self):
        with socket_lock:
            send_message(self.__transport, self.create_contacts_request(self.__client_name))
            answer = self.process_answer(get_message(self.__transport))

            return answer[MESSAGE]

    def get_clients_list(self):
        with socket_lock:
            send_message(self.__transport, self.create_clients_request(self.__client_name))
            answer = self.process_answer(get_message(self.__transport))

            return answer[MESSAGE]

    def add_contact(self, contact_name):
        with socket_lock:
            send_message(self.__transport, self.create_add_contacts_message(self.__client_name, contact_name))
            answer = self.process_answer(get_message(self.__transport))

            return answer[MESSAGE]

    def del_contact(self, contact_name):
        with socket_lock:
            send_message(self.__transport, self.create_del_contacts_message(self.__client_name, contact_name))
            answer = self.process_answer(get_message(self.__transport))

            return answer[MESSAGE]

    def run(self) -> None:
        pass
