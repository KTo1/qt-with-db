import sys
import json
import time
import socket

from select import select

from common.variables import (MAX_CONNECTIONS, RESPONSE, ERROR, TIME, USER, ACTION, ACCOUNT_NAME, PRESENCE,
                              DEFAULT_PORT, DEFAULT_IP_ADDRESS, MESSAGE, EXIT, TO_USERNAME, USERNAME_SERVER,
                              USERS_ONLINE)
from common.utils import get_message, send_message, parse_cmd_parameter
from logs.server_log_config import server_log
from logs.decorators import log


USERS_DB = ['Guest', 'Bazil', 'KTo', 'User']
USERS_ONLINE_DB = {}


@log
def process_client_message(message):
    """
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клиента, проверяет корректность,
    возвращает словарь-ответ для клиента
    """

    server_log.debug(f'Вызов функции "process_client_message", с параметрами: {str(message)}')

    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] in USERS_DB:
        return {RESPONSE: 200, MESSAGE: message}

    if ACTION in message and message[ACTION] == MESSAGE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] in USERS_DB:
        return {RESPONSE: 201, MESSAGE: message}

    if ACTION in message and message[ACTION] == EXIT and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] in USERS_DB:
        return {RESPONSE: 202, MESSAGE: message}

    if ACTION in message and message[ACTION] == USERS_ONLINE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] in USERS_DB:
        return {RESPONSE: 203, MESSAGE: message}

    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


@log
def create_presence_answer(response):
    """
    Генерирует ответ на приветствие
    :param response:
    :return:
    """

    return {
        RESPONSE: 200,
        TIME: time.time(),
        USER: response[MESSAGE][USER][ACCOUNT_NAME],
        MESSAGE: 'enter, and say hi all!'
    }


@log
def create_no_user_answer():
    """
    Генерирует сообщение пользователь не найден
    :param response:
    :return:
    """

    return {
        RESPONSE: 201,
        TIME: time.time(),
        USER: USERNAME_SERVER,
        MESSAGE: 'Пользователь не найден, возможно он не в сети, или вы ошиблись в имени.'
    }


@log
def create_user_online_answer():
    """
    Генерирует сообщение пользователи онлайн
    :param response:
    :return:
    """

    message = 'Список пользователей онлайн: \n'
    message += '\n'.join(['/' + user for user in USERS_ONLINE_DB])

    return {
        RESPONSE: 203,
        TIME: time.time(),
        USER: USERNAME_SERVER,
        MESSAGE: message
    }


@log
def create_answer(response):
    """
    Генерирует сообщение пользователю
    :param response:
    :return:
    """

    return {
        RESPONSE: 201,
        TIME: time.time(),
        USER: response[MESSAGE][USER][ACCOUNT_NAME],
        MESSAGE: response[MESSAGE][MESSAGE]
    }


@log
def create_exit_answer(response):
    """
    Генерирует сообщение выхода
    :param response:
    :return:
    """

    return {
        RESPONSE: 202,
        TIME: time.time(),
        USER: response[MESSAGE][USER][ACCOUNT_NAME],
        MESSAGE: 'exit and say by!'
    }


@log
def register_user_online(user, socket):
    USERS_ONLINE_DB[user] = socket


def unregister_user_online(user):
    del USERS_ONLINE_DB[user]


def get_socket_on_username(to_username):
    return USERS_ONLINE_DB.get(to_username.replace('/', ''))


def main():
    """
    Запускает сервер.
    Пример: server.py -p 8888 -a 127.0.0.1
    """

    listen_address = parse_cmd_parameter('-a', sys.argv, DEFAULT_IP_ADDRESS, 'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
    listen_port = parse_cmd_parameter('-p', sys.argv, DEFAULT_PORT, 'После параметра -\'p\' необходимо указать номер порта.')

    if listen_port is None or listen_address is None:
        server_log.error('Неверно заданы параметры командной строки')
        sys.exit(1)

    # process parameter
    try:
        listen_port = int(listen_port)
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except ValueError:
        server_log.exception('Номер порта может быть указано только в диапазоне от 1024 до 65535.')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))

    transport.listen(MAX_CONNECTIONS)
    transport.settimeout(1)

    clients_sockets = []
    server_log.info(f'Сервер запущен по адресу: {listen_address}: {listen_port}')

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
                        response = process_client_message(client_message)

                        # Пока так, 200 это приветствие
                        if response[RESPONSE] == 200 and client_socket in cl_sock_write:
                            send_message(client_socket, response)
                            register_user_online(response[MESSAGE][USER][ACCOUNT_NAME], client_socket)

                        # Пока так, 201 это сообщение
                        if response[RESPONSE] == 201:
                            user_socket = get_socket_on_username(response[MESSAGE][TO_USERNAME])
                            if user_socket:
                                message_pool.append((user_socket, create_answer(response)))
                            else:
                                message_pool.append((client_socket, create_no_user_answer()))

                        # Пока так, 202 это выход
                        if response[RESPONSE] == 202 and client_socket in cl_sock_write:
                            clients_sockets.remove(client_socket)
                            client_socket.close()
                            unregister_user_online(response[MESSAGE][USER][ACCOUNT_NAME])

                        # Пока так, 203 это запрос пользователей онлайн
                        if response[RESPONSE] == 203 and client_socket in cl_sock_write:
                            message_pool.append((client_socket, create_user_online_answer()))

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
    main()
