"""Лаунчер"""

import subprocess
from time import sleep

PROCESS = []
USERS = ['Guest', 'Bazil', 'KTo', 'User']


while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        PROCESS.append(subprocess.Popen('python server.py',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        sleep(3)

        for user in USERS:
            PROCESS.append(subprocess.Popen(f'python client.py -m send -u {user}',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))

        sleep(3)

        for user in USERS:
            PROCESS.append(subprocess.Popen(f'python client.py -m get -u {user}',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
