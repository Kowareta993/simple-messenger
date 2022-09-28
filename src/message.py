from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *
from datetime import datetime
from db import DB


class Message(QWidget):
    finished = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.sendBtn = QPushButton("send")
        self.sendBtn.clicked.connect(self.send)
        self.backBtn = QPushButton("back")
        self.backBtn.clicked.connect(lambda: self.finished.emit())
        self.receiver = QLineEdit()
        self.err = QLabel()
        self.items = 0
        self.msg = QLineEdit()
        self.create_layout()

    def get_users(self):
        users = [user[0] for user in DB().search_users("")]
        for i in range(self.items):
            self.userBtn.removeItem(i)
        self.userBtn.addItems(users)
        self.items = len(users)

    def create_layout(self):
        layout = QVBoxLayout()
        l = QHBoxLayout()
        l.addWidget(self.backBtn)
        l.addWidget(self.msg)
        l.addWidget(self.sendBtn)
        layout.addLayout(l)
        l2 = QHBoxLayout()
        l2.addWidget(QLabel("to: "))
        l2.addWidget(self.receiver)
        layout.addLayout(l2)
        layout.addWidget(self.err)
        self.setLayout(layout)

    def send(self):
        try:
            DB().send_msg(self.user, self.receiver.text(), self.msg.text(), datetime.now())
            self.err.setText("sent!")
        except Exception as e:
            self.err.setText(repr(e))
