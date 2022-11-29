import os
import configparser

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QLineEdit

from db.server_storage import ServerStorage


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'server_gui.ui'))


class ServerGui(QMainWindow, FORM_CLASS):
    
    def __init__(self, config_file_path):
        super(ServerGui, self).__init__()

        self.setupUi(self)

        self.__table_users_online_model = QStandardItemModel()
        self.__table_users_stat_model = QStandardItemModel()
        self.__table_users_online_header = ['Клиент', 'IP адрес', 'Порт', 'Подключен']
        self.__table_users_stat_header = ['Клиент', 'Вход', 'Отправлено', 'Получено']

        self.__timer = None
        self.__storage = ServerStorage()
        self.__config_file_path = config_file_path

        self.__load_config()

        self.initUi()

    def initUi(self):
        self.__table_users_online_model.setHorizontalHeaderLabels(self.__table_users_online_header)
        self.__table_users_stat_model.setHorizontalHeaderLabels(self.__table_users_stat_header)

        self.btn_save.clicked.connect(self.__save_config)
        self.table_users_online.setModel(self.__table_users_online_model)
        self.table_users_stat.setModel(self.__table_users_stat_model)

        self.lineEdit_pwd.setEchoMode(QLineEdit.Password)
        self.lineEdit_pwd2.setEchoMode(QLineEdit.Password)

    def __load_config(self):
        config = configparser.ConfigParser()
        config.read(self.__config_file_path)

        self.edt_database_dir.setText(config['SETTINGS']['database_dir'])
        self.edt_database_file.setText(config['SETTINGS']['database_file'])
        self.edt_default_address.setText(config['SETTINGS']['default_address'])
        self.edt_default_port.setText(config['SETTINGS']['default_port'])

    def __save_config(self):
        config = configparser.ConfigParser()
        config.read(self.__config_file_path)

        config['SETTINGS']['database_dir'] = self.edt_database_dir.text()
        config['SETTINGS']['database_file'] = self.edt_database_file.text()
        config['SETTINGS']['default_address'] = self.edt_default_address.text()
        config['SETTINGS']['default_port'] = self.edt_default_port.text()

        with open(self.__config_file_path, 'w') as f:
            config.write(f)

        self.status_message('Сохранено')

    def __on_timer_tic(self):
        self.load_user_table()
        self.load_stat_table()

    def status_message(self, message):
        self.statusbar.showMessage(message)

    def load_user_table(self):
        self.__table_users_online_model.clear()
        self.__table_users_online_model.setHorizontalHeaderLabels(self.__table_users_online_header)

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

    def load_stat_table(self):
        self.__table_users_stat_model.clear()
        self.__table_users_stat_model.setHorizontalHeaderLabels(self.__table_users_stat_header)

        stats = self.__storage.get_stat()
        for stat in stats:
            user, info, sent, recv = stat

            user = QStandardItem(user)
            info = QStandardItem(info)
            sent = QStandardItem(str(sent))
            recv = QStandardItem(str(recv))

            user.setEditable(False)
            info.setEditable(False)
            sent.setEditable(False)
            recv.setEditable(False)

            self.__table_users_stat_model.appendRow([user, info, sent, recv])

    def set_timer(self, interval):
        self.__timer = QTimer()
        self.__timer.timeout.connect(self.__on_timer_tic)
        self.__timer.start(interval)
