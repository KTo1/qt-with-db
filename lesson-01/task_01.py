# Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
# Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
# В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
# («Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
import time
import socket
import platform

from threading import Thread
from ipaddress import ip_address
from subprocess import Popen, PIPE


def host_ping_thread(ip_addr, result):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    args = ['ping', param, '2', ip_addr]
    reply = Popen(args, stdout=PIPE, stderr=PIPE)

    code = reply.wait()
    if code == 0:
        result['lucky'].append(str_address_to_ip_address(ip_addr))
    else:
        result['unlucky'].append(ip_addr)


def str_address_to_ip_address(address_string):
    try:
        ip_addr = ip_address(address_string)
    except ValueError:
        try:
            ip_addr = ip_address(socket.gethostbyname(address_string))
        except socket.gaierror:
            return None

    return ip_addr


def host_ping(address_list):
    threads = []
    result = {'lucky':[], 'unlucky': []}
    for address in address_list:
        thread = Thread(target=host_ping_thread, args=(address, result), daemon=True)
        thread.start()
        threads.append(thread)

    while True:
        enough = True
        time.sleep(1)
        for thread in threads:
            if thread.is_alive():
                enough = False
                break

        if not enough:
            continue
        break


    return result


if __name__ == '__main__':
    # address_list = ['yandex.ru', '127.0.0.1', 'no host', 'lovetou.ru']
    # print(host_ping(address_list))

    address = input('Введите адрес или имя хоста: ')
    result = host_ping([address])
    print('Узел недоступен' if result['unlucky'].count(address) > 0 else 'Узел доступен')