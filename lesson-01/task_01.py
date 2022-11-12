# Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
# Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
# В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
# («Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
import socket
import platform

from threading import Thread
from ipaddress import ip_address
from subprocess import Popen, PIPE


def host_ping(address_list):
    result = {'lucky':[], 'unlucky': []}
    for address in address_list:
        try:
            ip_addr = ip_address(address)
        except ValueError:
            try:
                ip_addr = ip_address(socket.gethostbyname(address))
            except socket.gaierror:
                result['unlucky'].append(address)
                continue

        param = '-n' if platform.system().lower() == 'windows' else '-c'
        args = ['ping', param, '2', str(ip_addr)]
        reply = Popen(args, stdout=PIPE, stderr=PIPE)

        code = reply.wait()
        result['lucky' if code == 0 else 'unlucky'].append(ip_addr)

    return result


if __name__ == '__main__':
    # address_list = ['yandex.ru', '127.0.0.1', 'no host']
    address = input('Введите адрес или имя хоста: ')
    print(host_ping([address]))