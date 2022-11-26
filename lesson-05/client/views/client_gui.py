import os
import time

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'client_gui.ui'))


class ClientGui(QMainWindow, FORM_CLASS):

    def __init__(self):
        super(ClientGui, self).__init__()

        self.setupUi(self)

    def initUi(self):
        self.__table_users_online_model.setHorizontalHeaderLabels(self.__table_users_online_header)
        self.__table_users_stat_model.setHorizontalHeaderLabels(self.__table_users_stat_header)

        self.pushButton_add_contact.clicked.connect(self.add_contact)
        self.pushButton_del_contact.clicked.connect(self.del_contact)
        self.pushButton_clear.clicked.connect(self.clear_message)
        self.pushButton_send.clicked.connect(self.send_message)

    def status_message(self, message):
        self.statusbar.showMessage(message)

    def add_contact(self):
        pass

    def del_contact(self):
        pass

    def clear_message(self):
        pass

    def send_message(self):
        pass

    def closeEvent(self, event):
        time.sleep(2)
        event.accept()