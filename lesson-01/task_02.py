# 2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона. Меняться должен только
# последний октет каждого адреса. По результатам проверки должно выводиться соответствующее сообщение.
from ipaddress import ip_address
from task_01 import host_ping


def host_range_ping(address, count):
    start_address = ip_address(address)

    start_octets = str(start_address).split('.')

    max_address = 256 - int(start_octets[3])
    if count > max_address:
        raise ValueError(f'Конечный адрес выходит за допустимый диапазон (max={max_address})!')

    return host_ping([start_address+i for i in range(max_address)])


if __name__ == '__main__':
    address = input('Введите начальный адрес: ')
    count = int(input('Введите количество адресов для проверки: '))

    print(host_range_ping(address, count))