from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *

from db import DB


class Register(QWidget):
    finished = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        # self.setGeometry(0, 0, 500, 500)
        self.username = QLineEdit()
        self.firstname = QLineEdit()
        self.lastname = QLineEdit()
        self.password = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.question = QLineEdit()
        self.button = QPushButton("register")
        self.button.clicked.connect(self.register)
        self.error = QLabel()
        self.create_layout()
        # self.setFixedSize(self.layout().sizeHint())

    def create_layout(self):
        layout = QFormLayout()
        layout.addRow(QLabel("username"), self.username)
        layout.addRow(QLabel("password"), self.password)
        layout.addRow(QLabel("firstname"), self.firstname)
        layout.addRow(QLabel("lastname"), self.lastname)
        layout.addRow(QLabel("phone"), self.phone)
        layout.addRow(QLabel("email"), self.email)
        layout.addRow(QLabel("security question"), self.question)
        layout.addRow(self.button)
        self.setLayout(layout)

    def register(self):
        data = {'username': self.username.text(), 'password': self.password.text(), 'firstname': self.firstname.text(),
                'lastname': self.lastname.text(), 'phone': self.phone.text(), 'email': self.email.text(),
                'security': self.question.text()}
        try:
            DB().register(data)
            self.finished.emit(0)
        except Exception as e:
            self.error.setText("Registration failed!\n" + repr(e))
            self.layout().addRow(self.error)
