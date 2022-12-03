import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))

from server_app import process_client_message
from common.variables import TIME, ACTION, PRESENCE, USER, ACCOUNT_NAME, RESPONSE, ERROR


class TestServer(unittest.TestCase):
    """
    Тест сервера
    """

    def setUp(self) -> None:
        pass

    err_dict = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }
    ok_dict = {RESPONSE: 200}

    def test_ok_check(self):
        """ Корректный запрос """
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.ok_dict)

    def test_no_action(self):
        """ Ошибка если нет действия """
        self.assertEqual(process_client_message(
            {TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_wrong_action(self):
        """ Ошибка если неизвестное действие """
        self.assertEqual(process_client_message(
            {ACTION: 'Wrong', TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_no_time(self):
        """ Ошибка, если запрос не содержит штампа времени """
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_no_user(self):
        """ Ошибка - нет пользователя """
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: '1.1'}), self.err_dict)

    def test_unknown_user(self):
        """ Ошибка - не Guest """
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest1'}}), self.err_dict)

    def test_empty_request(self):
        """ Ошибка - пустой запрос """
        self.assertEqual(process_client_message(''), self.err_dict)

    def tearDown(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()
