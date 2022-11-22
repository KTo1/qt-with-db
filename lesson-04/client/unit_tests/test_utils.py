import os
import sys
import json
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))

from common.utils import parse_cmd_parameter, send_message, get_message
from common.variables import TIME, ACTION, PRESENCE, USER, ACCOUNT_NAME, RESPONSE, ERROR, ENCODING


class TestSocket:
    """
    Тестовый класс для тестирования отправки и получения,
    при создании требует словарь, который будет прогоняться
    через тестовую функцию
    """

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message):
        """
        Тестовая функция отправки, корректно кодирует сообщение,
        так-же сохраняет то, что должно быть отправлено в сокет.
        message_to_send - то, что отправляем в сокет
        """

        json_test_message = json.dumps(self.test_dict)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.received_message = message

    def recv(self, max_package_length):
        """ Получаем данные из сокета """

        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class TestUtils(unittest.TestCase):
    """
    Тесты утилит
    """

    def setUp(self) -> None:
        self.test_dict_send = {
            ACTION: PRESENCE,
            TIME: 1.1,
            USER: {
                ACCOUNT_NAME: 'test_test'
            }
        }
        self.test_dict_recv_ok = {RESPONSE: 200}
        self.test_dict_recv_err = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    def test_parse_cmd_parameter_port(self):
        sys_argv = ['path', '-p', '8888', '-a', '127.0.0.1']
        self.assertEqual(parse_cmd_parameter('-p', sys_argv, 1111, 'Ошибка'), '8888')

    def test_parse_cmd_parameter_port_default(self):
        sys_argv = ['path', '-a', '127.0.0.1']
        self.assertEqual(parse_cmd_parameter('-p', sys_argv, 8888, 'Ошибка'), 8888)

    def test_parse_cmd_parameter_address(self):
        sys_argv = ['path', '-p', '8888', '-a', '127.0.0.1']
        self.assertEqual(parse_cmd_parameter('-a', sys_argv, '127.0.0.1', 'Ошибка'), '127.0.0.1')

    def test_parse_cmd_parameter_address_default(self):
        sys_argv = ['path', '-p', '8888']
        self.assertEqual(parse_cmd_parameter('-a', sys_argv, '127.0.0.1', 'Ошибка'), '127.0.0.1')

    def test_parse_cmd_parameter_error(self):
        sys_argv = ['path', '-p', '8888', '-a']
        self.assertRaises(IndexError, parse_cmd_parameter, '-a', sys_argv, 1111, 'Ошибка')

    def test_parse_cmd_parameter_empty(self):
        sys_argv = ''
        self.assertRaises(TypeError, parse_cmd_parameter, '-a', sys_argv, 1111, 'Ошибка')

    def test_send_message_true(self):
        """
        Тестируем корректность работы функции отправки,
        создадим тестовый сокет и проверим корректность отправки словаря
        """

        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)

    def test_send_message_with_error(self):
        """
        Тестируем корректность работы функции отправки,
        создадим тестовый сокет и проверим корректность отправки словаря
        """

        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        self.assertRaises(TypeError, send_message, test_socket, "wrong_dictionary")

    def test_get_message_ok(self):
        """ Тест функции приёма сообщения """

        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        self.assertEqual(get_message(test_sock_ok), self.test_dict_recv_ok)

    def test_get_message_error(self):
        """ Тест функции приёма сообщения """

        test_sock_err = TestSocket(self.test_dict_recv_err)
        self.assertEqual(get_message(test_sock_err), self.test_dict_recv_err)

    def tearDown(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()
