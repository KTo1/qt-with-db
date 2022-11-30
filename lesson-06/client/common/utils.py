import sys
import json
import hashlib
import binascii

from common.variables import MAX_PACKAGE_LENGTH, ENCODING, STRANGE_STRING
from logs.decorators import log, Log
from io import StringIO


class PortField:

    def __get__(self, instance, owner):
        return instance.__dict__[self.my_attr]

    def __set__(self, instance, value):
        if value < 1024 or value > 65535:
             raise ValueError(f'{self.my_attr} - может быть только в диапазоне от 1024 до 65535.')
        instance.__dict__[self.my_attr] = value

    def __delete__(self, instance):
        del instance.__dict__[self.my_attr]

    def __set_name__(self, owner, my_attr):
        self.my_attr = my_attr


def generate_hash(client_name, password):
    passwd_bytes = password.encode('utf-8')
    salt = (client_name + STRANGE_STRING).encode('utf-8')
    password_hash = hashlib.pbkdf2_hmac('sha512', passwd_bytes, salt, 10000)

    return binascii.hexlify(password_hash)


def result_from_stdout(func, arg):
    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    func(arg)
    result_string = result.getvalue()
    sys.stdout = old_stdout

    return result_string


@Log()
def parse_cmd_parameter(parameter, sys_argv, default_value, error_message):
    try:
        if not isinstance(sys_argv, list):
            raise TypeError
        if parameter in sys_argv:
            result = sys_argv[sys_argv.index(parameter) + 1]
        else:
            result = default_value

    except TypeError:
        result = None
        print('Второй параметр должен быть списком')
    except IndexError:
        result = None
        print(error_message)

    return result


@log
def send_message(socket, message):
    """
    Отправляет сообщение через сокет
    """

    if not isinstance(message, dict):
        raise TypeError

    json_string = json.dumps(message)
    message_bytes = json_string.encode(ENCODING)
    socket.send(message_bytes)


@log
def get_message(socket):
    """
    Получает сообщение из сокета, возвращает словарь с информацией о сообщении
    в случае ошибки выбрасывает ValueError
    """

    message_bytes = socket.recv(MAX_PACKAGE_LENGTH)
    if isinstance(message_bytes, bytes):
        json_string = message_bytes.decode(ENCODING)
        if isinstance(json_string, str):
            if not json_string:
                return {}
            message = json.loads(json_string)
            if isinstance(message, dict):
                return message

    raise ValueError
