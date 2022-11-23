import os

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow

from db.server_storage import ServerStorage


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'server_gui.ui'))


class ServerGui(QMainWindow, FORM_CLASS):
    
    def __init__(self):
        super(ServerGui, self).__init__()

        self.setupUi(self)

        self.__table_users_online_model = QStandardItemModel()
        self.__timer = None
        self.__storage = ServerStorage()

        self.initUi()

    def initUi(self):
        self.table_users_online.setModel(self.__table_users_online_model)

    def load_user_table(self):
        self.__table_users_online_model.clear()

        self.__table_users_online_model.setHorizontalHeaderLabels(['Клиент', 'IP адрес', 'Порт', 'Подключен'])

        clients_online = self.__storage.get_clients_online()
        for client in clients_online:
            ip, port, info, user = client
            user = QStandardItem(user)
            ip = QStandardItem(ip)
            port = QStandardItem(port)
            info = QStandardItem(info)

            user.setEditable(False)
            ip.setEditable(False)
            port.setEditable(False)
            info.setEditable(False)

            self.__table_users_online_model.appendRow([user, ip, port, info])

    def __on_timer_tic(self):
        self.load_user_table()

    def set_timer(self, interval):
        self.__timer = QTimer()
        self.__timer.timeout.connect(self.__on_timer_tic)
        self.__timer.start(interval)
