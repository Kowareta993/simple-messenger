from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *

from db import DB


class Profile(QWidget):
    clicked = pyqtSignal(int)
    finished = pyqtSignal(bool)

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.create_layout()

    def create_layout(self):
        layout = QGridLayout()
        layout.addWidget(QLabel(self.user), 0, 0, 2, 0)
        search = QPushButton("search")
        search.clicked.connect(lambda: self.clicked.emit(1))
        layout.addWidget(search, 1, 0)
        friends = QPushButton("friends")
        friends.clicked.connect(lambda: self.clicked.emit(2))
        layout.addWidget(friends, 1, 1)
        requests = QPushButton("requests")
        requests.clicked.connect(lambda: self.clicked.emit(3))
        layout.addWidget(requests, 2, 0)
        blocked = QPushButton("blocked users")
        blocked.clicked.connect(lambda: self.clicked.emit(4))
        layout.addWidget(blocked, 2, 1)
        message = QPushButton("send message")
        message.clicked.connect(lambda: self.clicked.emit(5))
        layout.addWidget(message, 3, 0)
        messages = QPushButton("show messages")
        messages.clicked.connect(lambda: self.clicked.emit(6))
        layout.addWidget(messages, 3, 1)
        delete = QPushButton("delete account")
        delete.clicked.connect(lambda: self.finished.emit(True))
        layout.addWidget(delete, 4, 0)
        logout = QPushButton("logout")
        logout.clicked.connect(lambda: self.finished.emit(False))
        layout.addWidget(logout, 4, 1)
        self.setLayout(layout)

