from server_log_config import server_log

import traceback


class Log():
    """ Декоратор лога классом """

    def __init__(self):
        self.__loggi = server_log

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            from_func_name = traceback.format_stack()[0].strip().split()[-1]
            self.__loggi.debug(f'Функция "{func.__name__}" вызвана c параметрами "args: {args}", "kwargs: {kwargs}"')
            self.__loggi.debug(f'Функция "{func.__name__}" вызвана из "{from_func_name}"')

            result = func(*args, **kwargs)

            return result

        return wrapper


def log(func):
    """ Декоратор лога функцией """

    loggi = server_log

    def wrapper(*args, **kwargs):
        from_func_name = traceback.format_stack()[0].strip().split()[-1]
        loggi.debug(f'Функция "{func.__name__}" вызвана c параметрами "args: {args}", "kwargs: {kwargs}"')
        loggi.debug(f'Функция "{func.__name__}" вызвана из "{from_func_name}"')

        result = func(*args, **kwargs)

        return result

    return wrapper