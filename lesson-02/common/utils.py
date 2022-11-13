import sys
import json
from common.variables import MAX_PACKAGE_LENGTH, ENCODING
from logs.decorators import log, Log


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
