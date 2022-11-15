import re
import dis
import sys
import json
import time
import socket
import threading

from common.variables import (DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, PRESENCE, TIME, USER,
                              ACCOUNT_NAME, RESPONSE, ERROR, DEFAULT_USER, MESSAGE, EXIT, TO_USERNAME, USERS_ONLINE)
from common.utils import get_message, send_message, parse_cmd_parameter, PortField
from common.exceptions import CodeException
from logs.client_log_config import client_log
from logs.decorators import log
from io import StringIO


class ClientVerifier(type):

    def __init__(self, *args, **kwargs):

        super(ClientVerifier, self).__init__(*args, **kwargs)

        for attr, val in args[2].items():
            if isinstance(val, socket.socket):
                raise CodeException('Сокеты в атрибутах запрещены.')

        re_tcp = r'.*LOAD_ATTR.*SOCK_STREAM.*'
        re_accept = r'.*LOAD_METHOD.*accept.*'
        re_listen = r'.*LOAD_METHOD.*listen.*'

        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result
        dis.dis(self)
        result_string = result.getvalue()
        sys.stdout = old_stdout

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

    def __init__(self, server_address, server_port, user_name):
        self.__server_address = server_address
        self.__server_port = server_port
        self.__user_name = user_name

    def create_common_message(self, account_name, action):
        result = {
            ACTION: action,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }

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

    def create_message(self, message, account_name, to_username):
        """
        Функция генерирует запрос о сообщении клиента
        :param message:
        :param account_name:
        :param to_username:
        :return:
        """

        result = self.create_common_message(account_name, MESSAGE)
        result[MESSAGE] = message
        result[TO_USERNAME] = to_username

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
            if answer[RESPONSE] == 200:
                return '200 : OK'

            if answer[RESPONSE] == 201 or answer[RESPONSE] == 202 or answer[RESPONSE] == 203:
                time_string = time.strftime('%d.%m.%Y %H:%M', time.localtime(answer[TIME]))
                return f'<{time_string}> {answer[USER]}: {answer[MESSAGE]}'

            return f'400 : {answer[ERROR]}'

        raise ValueError

    def print_help(self):
        """
        Выводит справку
        """

        help_string = 'Справка по командам:\n'
        help_string += '/help - эта справка\n'
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

    def send_messages(self, transport, user_name):
        """
        Для потока записи сообщений
        :param transport:
        :param user_name:
        :return:
        """

        while True:
            msg = input(f'<{user_name}> Введите непустое сообщение (/help - помощь): ')
            if not msg:
                continue

            if msg == '/exit' or msg == '.учше':
                send_message(transport, self.create_exit_message(user_name))
                print('Bye!')
                time.sleep(2)
                break

            if msg == '/help' or msg == '.рудз':
                self.print_help()
                continue

            if msg == '/online' or msg == '.щтдшту':
                send_message(transport, self.create_online_request(user_name))
                continue

            to_username = self.get_username_from_msg(msg)

            if to_username and not to_username == user_name:
                send_message(transport, self.create_message(msg.replace(to_username, ''), user_name, to_username))

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
                print(answer)


    def run(self):
        """
        Запускает клиент.
        -u User - имя пользователя
        Пример: client.py -u Guest -p 8888 -a 127.0.0.1
        Пример: client.py -u Guest -p 8888 -a 127.0.0.1
        """

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
            print(answer)

        except (ValueError, json.JSONDecodeError):
            client_log.exception('Не удалось декодировать сообщение сервера.')
            sys.exit(1)

        if answer == '200':
            pass

        sender = threading.Thread(target=self.send_messages, args=(transport, self.__user_name))
        receiver = threading.Thread(target=self.recv_messages, args=(transport,))

        sender.daemon = True
        receiver.daemon = True

        sender.start()
        receiver.start()

        while True:
            time.sleep(1)
            if sender.is_alive() and receiver.is_alive():
                continue
            break


if __name__ == '__main__':

    server_address = parse_cmd_parameter('-a', sys.argv, DEFAULT_IP_ADDRESS,
                                         'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
    server_port = parse_cmd_parameter('-p', sys.argv, DEFAULT_PORT,
                                      'После параметра -\'p\' необходимо указать номер порта.')
    user_name = parse_cmd_parameter('-u', sys.argv, DEFAULT_USER,
                                    'После параметра -\'u\' необходимо указать имя пользователя.')

    if server_port is None or server_address is None or user_name is None:
        raise ValueError('Неверно заданы параметры командной строки')

    # process parameter
    server_port1 = int(server_port)

    client = Client(server_address, server_port1, user_name)
    client.run()
