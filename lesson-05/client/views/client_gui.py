import os
import time

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow
from .add_contact import AddContactForm


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'client_gui.ui'))


class ClientGui(QMainWindow, FORM_CLASS):

    def __init__(self, transport):
        super(ClientGui, self).__init__()

        self.__transport = transport
        self.__table_contacts_model = QStandardItemModel()

        self.setupUi(self)
        self.initUi()
        self.update_contacts_list()

    def initUi(self):
        self.pushButton_add_contact.clicked.connect(self.add_contact_click)
        self.pushButton_del_contact.clicked.connect(self.del_contact)
        self.pushButton_clear.clicked.connect(self.clear_message)
        self.pushButton_send.clicked.connect(self.send_message)

        self.__add_contact_form = AddContactForm()
        self.__add_contact_form.buttonBox.accepted.connect(self.add_contact)

        self.table_contacts.setModel(self.__table_contacts_model)
        self.table_contacts.horizontalHeader().hide()
        self.table_contacts.horizontalHeader().setStretchLastSection(True)
        self.table_contacts.verticalHeader().hide()

    def update_contacts_list(self):
        self.__table_contacts_model.clear()

        clients_list = self.__transport.get_contacts_list()
        for client in clients_list:
            client_field = QStandardItem(client)
            client_field.setEditable(False)

            self.__table_contacts_model.appendRow([client_field])

    def status_message(self, message):
        self.statusbar.showMessage(message)

    def add_contact_click(self):
        clients_list = self.__transport.get_clients_list()
        self.__add_contact_form.set_clients_list(clients_list)
        self.__add_contact_form.show()

    def add_contact(self):
        contact = self.__add_contact_form.comboBox_contacts.currentText()
        self.__transport.add_contact(contact)
        self.update_contacts_list()

    def del_contact(self):
        select = self.table_contacts.selectionModel()
        if select.hasSelection():
            current_index = self.table_contacts.selectionModel().currentIndex()
            contact = self.__table_contacts_model.data(current_index)
            self.__transport.del_contact(contact)
            self.update_contacts_list()
        else:
            self.status_message('Выберите пользователя из списка.')

    def clear_message(self):
        pass

    def send_message(self):
        pass

    def closeEvent(self, event):
        self.status_message('Выход')
        time.sleep(2)
        event.accept()