import re
import dis
import socket

from .utils import result_from_stdout
from common.exceptions import CodeException


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