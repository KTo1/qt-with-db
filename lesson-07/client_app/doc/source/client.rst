Client module documentation
=================================================

Клиентское приложение для обмена сообщениями. Поддерживает
отправку сообщений пользователям которые находятся в сети.

Поддерживает аргументы командной строки:

``python client.py -a [имя сервера] -p [порт] -u [имя пользователя]``

1. -a [имя сервера] - адрес сервера сообщений.
2. -p [порт] - порт по которому принимаются подключения
3. -u [имя пользователя] имя пользователя с которым произойдёт вход в систему.


Все опции командной строки являются необязательными.
Адрес по умолчанию - 127.0.0.1
Порт по умолчанию - 8888


Примеры использования:

* ``python client.py``

*Запуск приложения с параметрами по умолчанию.*

* ``python client.py -a ip_address -p some_port``

*Запуск приложения с указанием подключаться к серверу по адресу ip_address:port*

* ``python client.py -p test1``

*Запуск приложения с пользователем test1*

client.py
~~~~~~~~~

.. automodule:: client
   :members:
   :undoc-members:
   :show-inheritance:
