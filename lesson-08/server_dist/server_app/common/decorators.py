""" Декораторы сервера"""

def login_required(func):
    """
    Декоратор, проверяющий, что клиент авторизован на сервере.
    Проверяет, что передаваемый объект сокета находится в
    списке авторизованных клиентов.
    За исключением передачи словаря-запроса
    на авторизацию. Если клиент не авторизован,
    генерирует исключение TypeError
    """

    def checker(*args, **kwargs):
        if func.__name__ == '__process_clients_messages':
            from server_app.common.variables import MESSAGE, ACTION, USER, ACCOUNT_NAME
            register_clients = args[0]._Server__clients_online_db
            client_name = args[2][MESSAGE][USER][ACCOUNT_NAME]
            action = args[2][MESSAGE][ACTION]

            if not action == 'presence':
                if not register_clients.get(client_name):
                    raise TypeError

        return func(*args, **kwargs)

    return checker
