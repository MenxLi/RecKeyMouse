from typing import List
from PyQt5 import QtCore
from PyQt5.QtWidgets import QAbstractItemView, QTableView, QWidget

from .logger import Logline

class EventEditor(QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent=parent)

    def initUI(self):
        pass

    def loadEventFile(self, f_path: str):
        pass

class EventViewer(QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent=parent)
    
    def initUI(self):
        pass

    def loadEvents(self, event_data: List[Logline]):
        pass


class EventTableModel(QtCore.QAbstractTableModel):
    def __init__(self, event_data: List[Logline]) -> None:
        super().__init__()


class EventTableView(QTableView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)