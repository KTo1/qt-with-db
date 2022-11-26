import os

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'client_gui.ui'))


class ClientGui(QMainWindow, FORM_CLASS):

    def __init__(self):
        super(ClientGui, self).__init__()

        self.setupUi(self)
