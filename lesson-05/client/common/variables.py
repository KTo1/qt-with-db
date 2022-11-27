""" Константы """

# Порт по умолчанию для сетевого взаимодействия
DEFAULT_PORT = 8888
# IP адрес по умолчанию
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключений
MAX_CONNECTIONS = 5
# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 4096
# Кодировка проекта
ENCODING = 'utf-8'

# Протокол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'

ACTION_GET_CONTACTS = 'get_contacts'
ACTION_GET_CLIENTS = 'get_clients'
ACTION_ADD_CONTACT = 'add_contact'
ACTION_DEL_CONTACT = 'del_contact'

# Прочие ключи, используемые в протоколе
USERNAME_SERVER = 'server'
USERS_ONLINE = 'users_online'
TO_USERNAME = 'to_username'
PRESENCE = 'presence'
MESSAGE = 'message'
RESPONSE = 'response'
ERROR = 'error'
EXIT = 'exit'