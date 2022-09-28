from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *

from db import DB


class Messages(QWidget):
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
        box = QGroupBox('messages')
        layout = QVBoxLayout()
        messages = DB().messages(self.user)
        for message in messages:
            entry = MessageEntry(message)
            layout.addWidget(entry)
        box.setLayout(layout)
        self.results.setWidget(box)

    def remove_friend(self, friend):
        DB().remove_friend(self.user, friend)


class MessageEntry(QWidget):
    liked = pyqtSignal(str)
    seen = pyqtSignal(str)

    def __init__(self, msg):
        super().__init__()
        self.id = msg[0]
        self.user = msg[1]
        self.text = QLabel(msg[3])
        self.time = msg[4]
        self.liked = int(msg[5])
        self.seen = int(msg[6])
        self.likeBtn = QPushButton("like")
        self.likeBtn.clicked.connect(self.like)
        self.seenBtn = QPushButton("seen")
        self.seenBtn.clicked.connect(self.see)
        self.create_layout()

    def create_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(self.user))
        layout.addWidget(self.text)
        layout.addWidget(QLabel(str(self.time)))
        l = QHBoxLayout()
        if self.seen == 1:
            l.addWidget(QLabel("seen"))
        else:
            l.addWidget(self.seenBtn)
        if self.liked == 1:
            l.addWidget(QLabel("liked"))
        else:
            l.addWidget(self.likeBtn)
        layout.addLayout(l)
        self.setLayout(layout)

    def like(self):
        DB().like(self.id)
        self.likeBtn.deleteLater()

    def see(self):
        DB().seen(self.id)
        self.seenBtn.deleteLater()
