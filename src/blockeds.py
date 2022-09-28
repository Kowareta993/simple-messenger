from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *

from db import DB


class Blockeds(QWidget):
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
        box = QGroupBox('blocked users')
        layout = QVBoxLayout()
        blockeds = DB().blocked_users(self.user)
        for user in blockeds:
            entry = Entry(user[0])
            entry.unblocked.connect(self.unblock)
            layout.addWidget(entry)
        box.setLayout(layout)
        self.results.setWidget(box)

    def unblock(self, user):
        DB().unblock(self.user, user)


class Entry(QWidget):
    unblocked = pyqtSignal(str)

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.unblockBtn = QPushButton("unblock")
        self.unblockBtn.clicked.connect(self.unblock)
        self.create_layout()

    def create_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(self.user))
        layout.addWidget(self.unblockBtn)
        self.setLayout(layout)

    def unblock(self):
        self.unblocked.emit(self.user)
        self.deleteLater()
