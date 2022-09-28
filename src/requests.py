from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *

from db import DB


class Requests(QWidget):
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
        box = QGroupBox('requests')
        layout = QVBoxLayout()
        requests = DB().requests(self.user)
        for request in requests:
            entry = RequestEntry(request[0])
            entry.accepted.connect(self.accept_request)
            layout.addWidget(entry)
        box.setLayout(layout)
        self.results.setWidget(box)

    def accept_request(self, user):
        DB().accept_request(user, self.user)


class RequestEntry(QWidget):
    accepted = pyqtSignal(str)

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.acceptBtn = QPushButton("accept")
        self.acceptBtn.clicked.connect(self.accept)
        self.create_layout()

    def create_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(self.user))
        layout.addWidget(self.acceptBtn)
        self.setLayout(layout)

    def accept(self):
        self.accepted.emit(self.user)
        self.deleteLater()
