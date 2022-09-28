import sys

from PyQt5.QtWidgets import *

from dashboard import Dashboard
from db import DB
from forget import Forget
from login import Login
from register import Register


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.user = None
        layout = QGridLayout()
        self.stack = QStackedWidget()
        login = Login()
        login.signed_in.connect(self.signed_in)
        login.new_acc.connect(self.register)
        login.forgot_pass.connect(self.forgot)
        self.stack.addWidget(login)
        register = Register()
        register.finished.connect(self.registered)
        self.stack.addWidget(register)
        layout.addWidget(self.stack)
        self.setLayout(layout)
        self.setWindowTitle("Messenger")

    def __del__(self):
        if self.user is None:
            return
        DB().logout(self.user)

    def signed_in(self, user):
        self.user = user
        dashboard = Dashboard(user)
        dashboard.finished.connect(self.signed_out)
        self.stack.insertWidget(2, dashboard)
        self.stack.setCurrentIndex(2)

    def forgot(self, user):
        forget = Forget(user)
        forget.finished.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.insertWidget(3, forget)
        self.stack.setCurrentIndex(3)

    def signed_out(self, deleted):
        DB().logout(self.user)
        if deleted:
            DB().delete_user(self.user)
        self.user = None
        self.stack.setCurrentIndex(0)

    def registered(self):
        self.stack.setCurrentIndex(0)

    def register(self):
        self.stack.setCurrentIndex(1)


def connect_database(init=False):
    db = DB()
    db.connect()
    if init:
        db.init_database()


def window():
    app = QApplication(sys.argv)
    w = MainWidget()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    if len(sys.argv) > 1:
        connect_database(True)
    else:
        connect_database()
    window()
