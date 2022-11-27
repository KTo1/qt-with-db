import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from .add_contact import AddContactForm


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'client_gui.ui'))


class ClientGui(QMainWindow, FORM_CLASS):

    def __init__(self, transport, storage, client_name):
        super(ClientGui, self).__init__()

        self.__transport = transport
        self.__storage = storage
        self.__client_name = client_name

        self.__table_contacts_model = QStandardItemModel()
        self.__table_messages_model = QStandardItemModel()

        self.__chat_with = ''
        self.__messages = QMessageBox()

        self.__color_red = QColor(255, 213, 213)
        self.__color_green = QColor(204, 255, 204)

        self.setupUi(self)
        self.initUi()
        self.setWindowTitle(f'Monsterchat client <{self.__client_name}>')

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
        self.table_contacts.doubleClicked.connect(self.select_dialog)

        self.table_messages.setModel(self.__table_messages_model)
        self.table_messages.horizontalHeader().hide()
        self.table_messages.horizontalHeader().setStretchLastSection(True)
        self.table_messages.verticalHeader().hide()

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

        if self.__messages.question(self, 'Удаление контакта', 'Вы уверены?', QMessageBox.Yes,
                                  QMessageBox.No) == QMessageBox.No:
            return

        select = self.table_contacts.selectionModel()
        if select.hasSelection():
            current_index = self.table_contacts.selectionModel().currentIndex()
            contact = self.__table_contacts_model.data(current_index)
            self.__transport.del_contact(contact)
            self.update_contacts_list()

            if self.__chat_with == contact:
                self.label_chat.setText(f'Чат с:  <>')
                self.pushButton_clear.setDisabled(True)
                self.pushButton_send.setDisabled(True)
                self.textEdit_message.setDisabled(True)

        else:
            self.status_message('Выберите пользователя из списка.')

    def select_dialog(self):
        if self.table_contacts.currentIndex().isValid():
            self.__chat_with = self.table_contacts.currentIndex().data()

            self.label_chat.setText(f'Чат с:  <{self.__chat_with}>')
            self.pushButton_clear.setDisabled(False)
            self.pushButton_send.setDisabled(False)
            self.textEdit_message.setDisabled(False)

            self.update_history()

    def update_history(self):
        messages = self.__storage.get_messages(20)

        self.__table_messages_model.clear()

        # Заполнение модели записями, так-же стоит разделить входящие и исходящие выравниванием и разным фоном.
        # Записи в обратном порядке, поэтому выбираем их с конца и не более 20
        for mes in messages:
            row = QStandardItem(f'{mes.date_action.replace(microsecond=0)}:\n {mes.message}')
            row.setEditable(False)

            if mes.login_from == self.__client_name:
                row.setBackground(QBrush(self.__color_red))
                row.setTextAlignment(Qt.AlignRight)
            else:
                row.setBackground(QBrush(self.__color_green))
                row.setTextAlignment(Qt.AlignLeft)

            self.__table_messages_model.appendRow(row)

        self.table_messages.scrollToBottom()

    def clear_message(self):
        self.__table_messages_model.clear()

    def send_message(self):
        message = self.textEdit_message.toPlainText()

        if not message:
            return
        try:
            self.__transport.send_message(self.__client_name, self.__chat_with, message)
            pass
        except OSError as err:
            if err.errno:
                self.status_message('Ошибка, потеряно соединение с сервером!')
                self.close()
            self.status_message('Ошибка, таймаут соединения!')
        except (ConnectionResetError, ConnectionAbortedError):
            self.status_message('Ошибка, потеряно соединение с сервером!')
        else:
            self.update_history()

    # Слот приёма нового сообщений
    @pyqtSlot(str)
    def new_message(self, sender):

        if sender == self.__chat_with:
            self.update_history()
        else:
            pass
        #     # Проверим есть ли такой пользователь у нас в контактах:
        #     if self.database.check_contact(sender):
        #         # Если есть, спрашиваем и желании открыть с ним чат и открываем при желании
        #         if self.messages.question(self, 'Новое сообщение', \
        #                                   f'Получено новое сообщение от {sender}, открыть чат с ним?', QMessageBox.Yes,
        #                                   QMessageBox.No) == QMessageBox.Yes:
        #             self.current_chat = sender
        #             self.set_active_user()
        #     else:
        #         print('NO')
        #         # Раз нету,спрашиваем хотим ли добавить юзера в контакты.
        #         if self.messages.question(self, 'Новое сообщение', \
        #                                   f'Получено новое сообщение от {sender}.\n Данного пользователя нет в вашем контакт-листе.\n Добавить в контакты и открыть чат с ним?',
        #                                   QMessageBox.Yes,
        #                                   QMessageBox.No) == QMessageBox.Yes:
        #             self.add_contact(sender)
        #             self.current_chat = sender
        #             self.set_active_user()

    # Слот потери соединения
    @pyqtSlot()
    def connection_lost(self):
        self.status_message('Сбой соединения, потеряно соединение с сервером. ')

    def make_connection(self, trans_obj):
        trans_obj.new_message.connect(self.new_message)
        trans_obj.connection_lost.connect(self.connection_lost)

    def closeEvent(self, event):
        event.accept()