import os

from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog, qApp


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'add_contact.ui'))


class AddContactForm(QDialog, FORM_CLASS):

    def __init__(self):
        super(AddContactForm, self).__init__()

        self.setupUi(self)

    def set_clients_list(self, clients_list):
        self.comboBox_contacts.clear()
        self.comboBox_contacts.addItems(clients_list)
