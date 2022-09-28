from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *

from db import DB


class Friends(QWidget):
    finished = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.showBtn = QPushButton("show")
        self.showBtn.clicked.connect(self.show)
        self.backBtn = QPushButton("back")
        self.backBtn.clicked.connect(lambda: self.finished.emit())
        self.results = QScrollArea()
        self.create_layout()

    def create_layout(self):
        layout = QVBoxLayout()
        l = QHBoxLayout()
        l.addWidget(self.backBtn)
        l.addWidget(self.showBtn)
        layout.addLayout(l)
        layout.addWidget(self.results)
        self.setLayout(layout)

    def show(self):
        box = QGroupBox('friends')
        layout = QVBoxLayout()
        friends = DB().friends(self.user)
        for friend in friends:
            u = friend[0] if friend[1] == self.user else friend[1]
            entry = FriendEntry(u)
            entry.removed.connect(self.remove_friend)
            layout.addWidget(entry)
        box.setLayout(layout)
        self.results.setWidget(box)

    def remove_friend(self, friend):
        DB().remove_friend(self.user, friend)


class FriendEntry(QWidget):
    removed = pyqtSignal(str)

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.removeBtn = QPushButton("remove")
        self.removeBtn.clicked.connect(self.remove)
        self.create_layout()

    def create_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(self.user))
        layout.addWidget(self.removeBtn)
        self.setLayout(layout)

    def remove(self):
        self.removed.emit(self.user)
        self.deleteLater()
