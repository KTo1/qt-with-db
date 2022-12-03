import os
import configparser

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QMessageBox
from datetime import datetime

from db.server_storage import ServerStorage
from common.utils import generate_hash


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'server_gui.ui'))


class ServerGui(QMainWindow, FORM_CLASS):
    
    def __init__(self, config_file_path):
        super(ServerGui, self).__init__()

        self.setupUi(self)

        self.__table_clients_online_model = QStandardItemModel()
        self.__table_clients_stat_model = QStandardItemModel()
        self.__table_clients_online_header = ['Клиент', 'IP адрес', 'Порт', 'Подключен']
        self.__table_clients_stat_header = ['Клиент', 'Вход', 'Отправлено', 'Получено']

        self.__timer = None
        self.__storage = ServerStorage()
        self.__config_file_path = config_file_path
        self.__messages = QMessageBox()

        self.__load_config()
        self.__load_client_list()

        self.initUi()

    def initUi(self):
        self.__table_clients_online_model.setHorizontalHeaderLabels(self.__table_clients_online_header)
        self.__table_clients_stat_model.setHorizontalHeaderLabels(self.__table_clients_stat_header)

        self.btn_save.clicked.connect(self.__save_config)
        self.table_clients_online.setModel(self.__table_clients_online_model)
        self.table_clients_stat.setModel(self.__table_clients_stat_model)

        self.lineEdit_pwd1.setEchoMode(QLineEdit.Password)
        self.lineEdit_pwd2.setEchoMode(QLineEdit.Password)

        self.pushButton_add_client.clicked.connect(self.__add_client_clicked)
        self.pushButton_del_client.clicked.connect(self.__del_client_clicked)

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
        self.load_client_table()
        self.load_stat_table()

    def __add_client_clicked(self):
        client_name = self.lineEdit_client_name.text().strip()
        pwd1 = self.lineEdit_pwd1.text()
        pwd2 = self.lineEdit_pwd2.text()

        if not client_name:
            self.status_message('Имя пользователя не указано.')
            return

        if not pwd1 == pwd2:
            self.status_message('Пароли не совпадают.')
            return

        if self.__storage.get_client_id(client_name):
            self.status_message('Такой пользователь уже существует.')
            return

        self.__storage.add_client(client_name, generate_hash(client_name, pwd1), datetime.now())

        self.lineEdit_client_name.setText('')
        self.lineEdit_pwd1.setText('')
        self.lineEdit_pwd2.setText('')

        self.__load_client_list()

        self.status_message('Пользователь добавлен.')

    def __del_client_clicked(self):
        if self.__messages.question(self, 'Удаление контакта', 'Вы уверены?', QMessageBox.Yes,
                                  QMessageBox.No) == QMessageBox.No:
            return

        client_name = self.comboBox_clients.currentText()
        client_id = self.__storage.get_client_id(client_name)

        if not client_name:
            self.status_message('Пользователь не найден, возможно он уже удален.')
            self.__load_client_list()
            return

        self.__storage.del_client(client_id)
        self.__load_client_list()

    def __load_client_list(self):
        self.comboBox_clients.clear()
        self.comboBox_clients.addItems(self.__storage.get_register_clients())

    def status_message(self, message):
        self.statusbar.showMessage(message)

    def load_client_table(self):
        self.__table_clients_online_model.clear()
        self.__table_clients_online_model.setHorizontalHeaderLabels(self.__table_clients_online_header)

        clients_online = self.__storage.get_clients_online()
        for elem in clients_online:
            ip, port, info, client = elem

            client = QStandardItem(client)
            ip = QStandardItem(ip)
            port = QStandardItem(port)
            info = QStandardItem(info)

            client.setEditable(False)
            ip.setEditable(False)
            port.setEditable(False)
            info.setEditable(False)

            self.__table_clients_online_model.appendRow([client, ip, port, info])

    def load_stat_table(self):
        self.__table_clients_stat_model.clear()
        self.__table_clients_stat_model.setHorizontalHeaderLabels(self.__table_clients_stat_header)

        stats = self.__storage.get_stat()
        for elem in stats:
            client, info, sent, recv = elem

            client = QStandardItem(client)
            info = QStandardItem(info)
            sent = QStandardItem(str(sent))
            recv = QStandardItem(str(recv))

            client.setEditable(False)
            info.setEditable(False)
            sent.setEditable(False)
            recv.setEditable(False)

            self.__table_clients_stat_model.appendRow([client, info, sent, recv])

    def set_timer(self, interval):
        self.__timer = QTimer()
        self.__timer.timeout.connect(self.__on_timer_tic)
        self.__timer.start(interval)
