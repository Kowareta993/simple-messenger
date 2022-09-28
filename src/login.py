from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *

from db import DB


class Login(QWidget):
    signed_in = pyqtSignal(str)
    forgot_pass = pyqtSignal(str)
    new_acc = pyqtSignal()

    def __init__(self):
        super().__init__()
        # self.setGeometry(0, 0, 500, 500)
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.loginBtn = QPushButton("login")
        self.loginBtn.clicked.connect(self.login)
        self.registerBtn = QPushButton("register")
        self.registerBtn.clicked.connect(self.register)
        self.forgotBtn = QPushButton("forgot password")
        self.forgotBtn.clicked.connect(self.forgot)
        self.error = QLabel()
        self.create_layout()

        # self.setFixedSize(self.layout().sizeHint())

    def create_layout(self):
        layout = QFormLayout()
        layout.addRow(QLabel("username"), self.username)
        layout.addRow(QLabel("password"), self.password)
        layout.addRow(self.loginBtn)
        layout.addRow(self.forgotBtn)
        layout.addRow(self.registerBtn)
        self.setLayout(layout)

    def login(self):
        data = {'username': self.username.text(), 'password': self.password.text()}
        user = DB().login(data)
        if user is None:
            self.error.setText("Login failed!\n")
            self.layout().addRow(self.error)
            return
        self.signed_in.emit(user)

    def register(self):
        self.new_acc.emit()

    def forgot(self):
        self.forgot_pass.emit(self.username.text())
