from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *
from datetime import datetime
from db import DB


class Forget(QWidget):
    finished = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.sendBtn = QPushButton("recover")
        self.sendBtn.clicked.connect(self.security)
        self.sendBtn2 = QPushButton("recover")
        self.sendBtn2.clicked.connect(self.recover)
        self.backBtn = QPushButton("back")
        self.backBtn.clicked.connect(lambda: self.finished.emit())
        self.answer = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.err1 = QLabel()
        self.err2 = QLabel()
        self.create_layout()

    def create_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(self.backBtn)
        l = QVBoxLayout()
        l.addWidget(QLabel("security answer: "))
        l.addWidget(self.answer)
        l.addWidget(self.sendBtn)
        l.addWidget(self.err1)
        layout.addLayout(l)
        l2 = QVBoxLayout()
        l2.addWidget(QLabel("email: "))
        l2.addWidget(self.email)
        l2.addWidget(QLabel("phone: "))
        l2.addWidget(self.phone)
        l2.addWidget(self.sendBtn2)
        l2.addWidget(self.err2)
        layout.addLayout(l2)
        self.setLayout(layout)

    def security(self):
        result = DB().security_answer(self.user, self.answer.text())
        if result is None:
            self.err1.setText("wrong!")
        else:
            self.err1.setText(f"pass: {result}")

    def recover(self):
        result = DB().pass_recovery(self.user, self.email.text(), self.phone.text())
        if result is None:
            self.err2.setText("wrong!")
        else:
            self.err2.setText(f"pass: {result}")
