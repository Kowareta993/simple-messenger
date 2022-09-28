from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *

from db import DB


class Search(QWidget):
    finished = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        # self.setGeometry(0, 0, 500, 500)
        self.user = user
        self.results = None
        self.input = None
        self.msg = None
        self.create_layout()

        # self.setFixedSize(self.layout().sizeHint())

    def create_layout(self):
        layout1 = QHBoxLayout()
        layout2 = QVBoxLayout()
        back = QPushButton("back")
        back.clicked.connect((lambda: self.finished.emit()))
        layout1.addWidget(back)
        self.input = QLineEdit()
        layout1.addWidget(self.input)
        search = QPushButton("search")
        search.clicked.connect(self.search)
        layout1.addWidget(search)
        layout2.addLayout(layout1)
        self.results = QScrollArea()
        layout2.addWidget(self.results)
        self.msg = QLabel()
        layout2.addWidget(self.msg)
        self.setLayout(layout2)

    def search(self):
        results = DB().search_users(self.input.text())
        box = QGroupBox("result")
        layout = QVBoxLayout()
        for result in results:
            entry = UserEntry(result[0])
            entry.add.connect(self.add)
            entry.block.connect(self.block)
            layout.addWidget(entry)
        box.setLayout(layout)
        self.results.setWidget(box)

    def add(self, user):
        try:
            DB().send_request(self.user, user)
            self.msg.setText(f"request sent to {user}")
        except Exception as e:
            self.msg.setText(repr(e))

    def block(self, user):
        try:
            DB().block(self.user, user)
            self.msg.setText(f"{user} blocked")
        except Exception as e:
            self.msg.setText(repr(e))


class UserEntry(QWidget):
    removed = pyqtSignal(str)
    add = pyqtSignal(str)
    block = pyqtSignal(str)

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.addBtn = QPushButton("add")
        self.addBtn.clicked.connect(lambda: self.add.emit(self.user))
        self.blockBtn = QPushButton("block")
        self.blockBtn.clicked.connect(lambda: self.block.emit(self.user))
        self.msg = QLabel()
        self.create_layout()

    def create_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(self.user))
        layout.addWidget(self.addBtn)
        layout.addWidget(self.blockBtn)
        self.setLayout(layout)
