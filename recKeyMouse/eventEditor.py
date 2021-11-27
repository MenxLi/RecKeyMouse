from typing import List, Tuple, Union
import typing
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QAbstractItemView, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton, QShortcut, QTableView, QVBoxLayout, QWidget

from .logger import ActionLogger, Logline
from .utils import deleteDuplicate

class EventEditor(QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent=parent)
        self.initUI()

    def initUI(self):
        self.resize(500, 500)
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
        hhbox = QHBoxLayout()
        label = QLabel(self.event_name)
        self.event_view = EventTableView()
        self.btn_delete = QPushButton("Delete")
        self.btn_edit = QPushButton("Edit")

        self.btn_delete.clicked.connect(self.deleteCurrentSelected)
        self.btn_edit.clicked.connect(self.openEditor)

        vbox.addWidget(label)
        vbox.addWidget(self.event_view)
        vbox.addLayout(hhbox)
        hhbox.addWidget(self.btn_edit)
        hhbox.addWidget(self.btn_delete)

        frame.setLayout(vbox)
        self.setLayout(main_layout)

        ## not working?
        # self.shortcut_delete_selections = QShortcut(QtGui.QKeySequence("Del"), self)
        # self.shortcut_delete_selections.activated.connect(self.deleteCurrentSelected)

    def loadEvents(self, event_data: List[Logline]):
        self.model = EventTableModel(event_data)
        self.event_view.setModel(self.model)
        self.event_view.initSettings()
    
    def openEditor(self):
        indexes = self.getCurrentSelectIdx()
        if indexes is None:
            return
        for index in indexes:
            def callback(data: Logline):
                self.model.data[index] = data
                self.model.data.sort(key=lambda x: x["time"])
                return None
            self.editor = SingleEventEditor(self.model.data[index], callback)
    
    def deleteCurrentSelected(self):
        indexes = self.getCurrentSelectIdx()
        if indexes is None:
            return
        indexes.sort(reverse=True)
        for i in indexes:
            print("deleted ==>", self.model.data[i])
            self.model.data.pop(i)
            self.model.layoutChanged.emit()
    
    def getCurrentSelectIdx(self) -> Union[List[int], None]:
        indexes = self.event_view.selectedIndexes()
        if indexes == [] or not indexes:
            return None
        try:
            rows = [index.row() for index in indexes]
            rows = deleteDuplicate(rows)
            rows.sort()
            return rows
        except:
            # When index is larger than the length of the data
            return None


class EventTableModel(QtCore.QAbstractTableModel):
    # https://www.pythonguis.com/tutorials/qtableview-modelviews-numpy-pandas/
    def __init__(self, event_data: List[Logline]) -> None:
        super().__init__()
        self.data: List[Logline] = event_data

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

class SingleEventEditor(QWidget):
    def __init__(self, data: Logline, accept_callback: typing.Callable) -> None:
        super().__init__()
        self.data:Logline = data
        self.data_widgets:List[Tuple[QLabel, QLineEdit, Union[float, str, list, dict]]] = list()  # [QLabel, QLineEdit, Original Data]
        print("Open editor for: ", str(data))
        self.initUI()
        self.accept_callback = accept_callback
    
    def initUI(self):
        vbox = QVBoxLayout()
        for k, v in self.data.items():
            hbox = QHBoxLayout()
            label = QLabel(k)
            line_edit = QLineEdit()
            line_edit.setText(Logline.INDEX_FUNC_DICT[k](self.data))
            hbox.addWidget(label)
            hbox.addWidget(line_edit)
            vbox.addLayout(hbox)

            self.data_widgets.append((label, line_edit, v))
        self.btn_accept = QPushButton("Accept")
        self.btn_accept.clicked.connect(self.accept)
        vbox.addWidget(self.btn_accept)
        self.setLayout(vbox)
        self.show()
    
    def accept(self):
        new_data = {}
        for i in self.data_widgets:
            name = i[0].text()
            text = i[1].text()
            value = Logline.REVERSE_FUNC_DICT[name](text)
            new_data[name] = value
        new_data = Logline(new_data)
        print("New event: ", new_data)
        self.accept_callback(new_data)
        self.close()