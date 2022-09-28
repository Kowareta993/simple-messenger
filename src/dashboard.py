from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *

from blockeds import Blockeds
from friends import Friends
from message import Message
from messages import Messages
from profile import Profile
from requests import Requests
from search import Search


class Dashboard(QWidget):
    finished = pyqtSignal(bool)
    search = pyqtSignal()
    update = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.stack = QStackedWidget()
        self.profile = Profile(user)
        self.profile.clicked.connect(self.change)
        self.profile.finished.connect(self.logout)
        self.stack.insertWidget(0, self.profile)
        self.search = Search(user)
        self.search.finished.connect(self.home)
        self.stack.insertWidget(1, self.search)
        self.friends = Friends(user)
        self.friends.finished.connect(self.home)
        self.stack.insertWidget(2, self.friends)
        self.requests = Requests(user)
        self.stack.insertWidget(3, self.requests)
        self.requests.finished.connect(self.home)
        self.blockeds = Blockeds(user)
        self.stack.insertWidget(4, self.blockeds)
        self.blockeds.finished.connect(self.home)
        self.message = Message(user)
        self.stack.insertWidget(5, self.message)
        self.message.finished.connect(self.home)
        self.messages = Messages(user)
        self.stack.insertWidget(6, self.messages)
        self.messages.finished.connect(self.home)
        self.create_layout()

    def home(self):
        self.stack.setCurrentIndex(0)

    def change(self, i):
        self.stack.setCurrentIndex(i)

    def create_layout(self):
        layout = QGridLayout()
        self.stack.setCurrentIndex(0)
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def logout(self, deleted):
        self.finished.emit(deleted)
