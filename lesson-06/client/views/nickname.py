import os
import configparser

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QDialog, qApp, QLineEdit

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'nickname.ui'))


class NicknameForm(QDialog, FORM_CLASS):

    def __init__(self):
        super(NicknameForm, self).__init__()

        self.setupUi(self)
        self.initUi()

        self.ok_pressed = False

    def initUi(self):
        self.lineEdit_pwd.setEchoMode(QLineEdit.Password)

    def accept(self) -> None:
        self.ok_pressed = True
        qApp.exit()

    def reject(self) -> None:
        self.ok_pressed = False
        qApp.exit()
