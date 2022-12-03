import os
import sys
sys.path.append(os.path.join(os.getcwd(), '..'))
import unittest

from client import create_presence, process_answer
from common.variables import TIME, ACTION, PRESENCE, USER, ACCOUNT_NAME, RESPONSE, ERROR


class TestClient(unittest.TestCase):
    """
    Тест клиента
    """

    def setUp(self) -> None:
        pass

    def test_create_presence_default(self):
        """ Тест приветствия с именем пользователя по умолчанию """

        test_presence = create_presence()
        test_presence[TIME] = 1.1

        self.assertEqual(test_presence, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME:'Guest'}})

    def test_create_presence(self):
        """ Тест приветствия с заданным именем пользователя """

        test_presence = create_presence('user_1')
        test_presence[TIME] = 1.1

        self.assertEqual(test_presence, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME:'user_1'}})

    def test_200_answer(self):
        """ Тест корректного разбора ответа 200 """
        self.assertEqual(process_answer({RESPONSE: 200}), '200 : OK')

    def test_400_answer(self):
        """ Тест корректного разбора 400 """
        self.assertEqual(process_answer({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        """Тест исключения без поля RESPONSE"""
        self.assertRaises(ValueError, process_answer, {ERROR: 'Bad Request'})

    def tearDown(self) -> None:
        pass

if __name__ == '__main__':
    unittest.main()

