from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QMainWindow, QPushButton, QWidget

from recKeyMouse.executer import Executer
from .logger import ActionLogger
from .confReader import getConf
import json, os


class RecorderWindow(QMainWindow):
    def __init__(self, parent = None, saving_path:str = None) -> None:
        super().__init__(parent=parent)
        if saving_path is None:
            log_path = getConf("log_path")
        else:
            log_path = saving_path
        log_path = os.path.abspath(log_path)
        self.logger = ActionLogger(log_path)
        self.initUI()
    
    def initUI(self):
        vbox = QVBoxLayout()
        self.setMaximumWidth(300)
        self.lbl_logpath = QLabel()
        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.btn_run = QPushButton("Run")

        vbox.addWidget(self.lbl_logpath)
        vbox.addWidget(self.btn_start)
        vbox.addWidget(self.btn_stop)
        vbox.addWidget(self.btn_run)
        
        wid = QWidget()
        self.setCentralWidget(wid)
        wid.setLayout(vbox)

        self.lbl_logpath.setWordWrap(True)
        self.lbl_logpath.setText(f"log file: {self.logger.record_file}")

        self.btn_start.pressed.connect(self.startRecording)
        self.btn_stop.pressed.connect(self.stopRecording)
        self.btn_run.pressed.connect(self.exectueRecord)
        self.show()
    
    def startRecording(self):
        # self.showNormal()
        # self.showMinimized()
        self.logger.start()
    
    def stopRecording(self):
        record = self.logger.stop()
        record["mouse_events"].pop()    # Delete last key press
        self.logger.writeLog(record)
    
    def exectueRecord(self):
        executer = Executer(self.logger.record_file)
        executer.run()
