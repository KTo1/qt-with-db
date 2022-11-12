# 3. Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
# Но в данном случае результат должен быть итоговым по всем ip-адресам, представленным в табличном формате
# (использовать модуль tabulate). Таблица должна состоять из двух колонок и выглядеть примерно так:
# Reachable
# 10.0.0.1
# 10.0.0.2
#
# Unreachable
# 10.0.0.3
# 10.0.0.4
from task_02 import host_range_ping
from tabulate import tabulate


if __name__ == '__main__':
    address = input('Введите начальный адрес: ')
    count = int(input('Введите количество адресов для проверки: '))

    print(tabulate(host_range_ping(address, count), headers='keys'))