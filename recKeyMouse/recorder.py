import threading, multiprocessing
from time import time, sleep
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QCursor, QFont, QIcon
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QTextEdit, QVBoxLayout, QMainWindow, QPushButton, QWidget

from recKeyMouse.executer import Executer
from .logger import ActionLogger
from .confReader import getConf, ICON_PATH
import json, os, sys


class RecorderWindow(QMainWindow):
    def __init__(self, parent = None, saving_path:str = None) -> None:
        super().__init__(parent=parent)
        if saving_path is None:
            log_path = getConf("log_path")
        else:
            log_path = saving_path
        sys.stdout = EmittingStream(textWritten = self.stdoutStream)
        log_path = os.path.abspath(log_path)
        self.logger = ActionLogger(log_path)
        self.initUI()

        self.__thread_startRecording = None
        self.__thread_stopRecording = None
        self.__thread_executeRecord = None

        def watchRecordingStatus():
            prev_recording = False
            while True:
                if self.logger.cache["recording"] and not prev_recording:
                    self.btn_start_stop.setIcon(QIcon(os.path.join(ICON_PATH, "round_stop_black_48dp.png")))
                    self.btn_start_stop.setText("Stop")
                    prev_recording = True
                elif not self.logger.cache["recording"] and prev_recording: 
                    self.btn_start_stop.setIcon(QIcon(os.path.join(ICON_PATH, "round_play_arrow_black_48dp.png")))
                    self.btn_start_stop.setText("Start")
                    prev_recording = False
                sleep(0.2)
        threading.Thread(target=watchRecordingStatus, daemon=True).start()
    
    def initUI(self):
        vbox = QVBoxLayout()
        self.setWindowTitle("recKeyMouse")
        self.setMaximumWidth(300)
        self.lbl_logpath = QLabel()
        self.btn_start_stop = QPushButton("Start")
        self.btn_start_stop.setIcon(QIcon(os.path.join(ICON_PATH, "round_play_arrow_black_48dp.png")))
        self.btn_run = QPushButton("Run (x{})".format(getConf("replay_times")))
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("color: white; background-color:black")
        self.console.setFont(QFont('Courier', 10))

        vbox.addWidget(self.lbl_logpath)
        vbox.addWidget(self.btn_start_stop)
        vbox.addWidget(self.btn_run)
        vbox.addWidget(self.console)
        
        wid = QWidget()
        self.setCentralWidget(wid)
        wid.setLayout(vbox)

        self.lbl_logpath.setWordWrap(True)
        self.lbl_logpath.setText(f"log file: {self.logger.record_file}")

        self.btn_start_stop.pressed.connect(self.startStopRecording)
        self.btn_run.pressed.connect(self.exectueRecord)
        self.show()
    
    def startStopRecording(self):
        if self.logger.cache["recording"]:
            self.stopRecording()
        else:
            self.startRecording()
    
    def startRecording(self):
        # self.showNormal()
        # self.showMinimized()
        if isinstance(self.__thread_startRecording, threading.Thread):
            if self.__thread_startRecording.is_alive():
                print("Thread is running, waiting for the thread to stop.")
                return
        self.__thread_startRecording = threading.Thread(target=self.logger.start)
        self.__thread_startRecording.start()
        # self.logger.start()
    
    def stopRecording(self):
        if isinstance(self.__thread_stopRecording, threading.Thread):
            if self.__thread_stopRecording.is_alive():
                print("Thread is running, waiting for the thread to stop.")
                return
        def _stopRecording():
            record = self.logger.stop()
            record["mouse_events"].pop()    # Delete last key press
            self.logger.writeLog(record)
        self.__thread_stopRecording = threading.Thread(target=_stopRecording)
        self.__thread_stopRecording.start()
    
    def exectueRecord(self):
        if isinstance(self.__thread_executeRecord, threading.Thread):
            if self.__thread_executeRecord.is_alive():
                print("Thread is running, waiting for the thread to stop.")
                return
        def _executeRecord():
            executer = Executer(self.logger.record_file)
            executer.run(getConf("replay_times"))
        self.__thread_executeRecord = threading.Thread(target=_executeRecord)
        self.__thread_executeRecord.start()
    
    def stdoutStream(self, text):
        self.console.insertPlainText(text)
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

class EmittingStream(QObject):
    """Reference: https://stackoverflow.com/questions/8356336/how-to-capture-output-of-pythons-interpreter-and-show-in-a-text-widget"""
    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))