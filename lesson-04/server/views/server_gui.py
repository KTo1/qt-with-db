import os
import configparser

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow

from db.server_storage import ServerStorage


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'server_gui.ui'))


class ServerGui(QMainWindow, FORM_CLASS):
    
    def __init__(self, config_file_path):
        super(ServerGui, self).__init__()

        self.setupUi(self)

        self.__table_users_online_model = QStandardItemModel()
        self.__timer = None
        self.__storage = ServerStorage()
        self.__config_file_path = config_file_path

        self.__load_config()

        self.initUi()

    def initUi(self):
        self.btn_save.clicked.connect(self.__save_config)
        self.table_users_online.setModel(self.__table_users_online_model)

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

    def status_message(self, message):
        self.statusbar.showMessage(message)

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

    def set_timer(self, interval):
        self.__timer = QTimer()
        self.__timer.timeout.connect(self.__on_timer_tic)
        self.__timer.start(interval)
