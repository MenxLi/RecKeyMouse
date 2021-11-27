from typing import List
from PyQt5 import QtCore
from PyQt5.QtWidgets import QAbstractItemView, QFrame, QHBoxLayout, QHeaderView, QLabel, QTableView, QVBoxLayout, QWidget

from .logger import ActionLogger, Logline

class EventEditor(QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent=parent)
        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()
        self.mouse_viewer = EventViewer("Mouse events")
        self.keyboard_viewer = EventViewer("Keyboard events")
        vbox.addWidget(self.mouse_viewer)
        vbox.addWidget(self.keyboard_viewer)
        self.setLayout(vbox)
        self.show()

    def loadEventFile(self, f_path: str):
        self.logger = ActionLogger(f_path)
        self.logger.loadLog()
        self.mouse_viewer.loadEvents(self.logger.mouse_events)
        self.keyboard_viewer.loadEvents(self.logger.keyboard_events)

class EventViewer(QWidget):
    def __init__(self, event_name = "event") -> None:
        super().__init__()
        self.event_name = event_name
        self.initUI()
    
    def initUI(self):
        main_layout = QHBoxLayout()
        frame = QFrame()
        main_layout.addWidget(frame)

        vbox = QVBoxLayout()
        label = QLabel(self.event_name)
        self.event_view = EventTableView()

        vbox.addWidget(label)
        vbox.addWidget(self.event_view)

        frame.setLayout(vbox)
        self.setLayout(main_layout)

    def loadEvents(self, event_data: List[Logline]):
        self.model = EventTableModel(event_data)
        self.event_view.setModel(self.model)
        self.event_view.initSettings()


class EventTableModel(QtCore.QAbstractTableModel):
    # https://www.pythonguis.com/tutorials/qtableview-modelviews-numpy-pandas/
    def __init__(self, event_data: List[Logline]) -> None:
        super().__init__()
        self.data = event_data

    def data(self, index: QtCore.QModelIndex, role):
        if role == QtCore.Qt.DisplayRole:
            return self.data[index.row()].getStrItemByIndex(index.column())
    
    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self.data)

    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(Logline.INDEX_FUNC)
    
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(Logline.INDEX_FUNC[section][0])

            if orientation == QtCore.Qt.Vertical:
                return str(section)

class EventTableView(QTableView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    def initSettings(self):
        for i in range(len(Logline.INDEX_FUNC)):
            self.header = self.horizontalHeader()
            self.header.setSectionResizeMode(i, QHeaderView.Stretch)