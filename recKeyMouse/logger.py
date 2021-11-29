from io import TextIOWrapper
from time import ctime, time, sleep
import pickle, threading, os

import pynput
from pynput import mouse
from pynput import keyboard
from pynput.mouse import Controller as M_Controller
from pynput.mouse import Button as M_Button
from .confReader import getConf

from .logUtils import Logline, generateLogLine

class ActionLogger():
    MOUSE_MOVE_TIME_INTERVAL = 0.05
    MOUSE_MOVE_DISTANCE_SQUARED = 2500
    STOP_KEY = pynput.keyboard.Key.esc
    def __init__(self, log_file: str, log_mouse_motion = getConf("record_mouse_motion")) -> None:
        if os.path.isdir(log_file):
            log_file = os.path.join(log_file, "record.pkl")
        self.record_file = os.path.abspath(log_file)
        # self.mouse_events = []
        # self.keyboard_events = []
        self.events = []
        self.log_mouse_motion = log_mouse_motion
        self.cache = {
            "thread_started": False,
            "recording": False,
            "mouse_pressed": False,
            "mouse_move_logtime" : 0, 
            "mouse_prev_pos": (0, 0)
        }
        self.threads = []

    def onMouseMove(self, x, y):
        if not self.log_mouse_motion and not self.cache["mouse_pressed"]: return
        if not self.cache["recording"]: return
        _time = time() - self.start_time
        if _time - self.cache["mouse_move_logtime"]> self.MOUSE_MOVE_TIME_INTERVAL:
            self._onMouseMove(x, y, _time)
            return
        prev_x, prev_y = self.cache["mouse_prev_pos"]
        mouse_move_distance_sqr = (x-prev_x)**2 + (y-prev_y)**2
        if mouse_move_distance_sqr > self.MOUSE_MOVE_DISTANCE_SQUARED:
            self._onMouseMove(x, y, _time)
            return
    
    def _onMouseMove(self, x, y, _time):
        self.cache["mouse_move_logtime"] = _time
        self.cache["mouse_prev_pos"] = (x, y)
        log_dict = generateLogLine(_time, "Mouse", "setPos", [x,y], kwargs={})
        self.events.append(log_dict)

    def onMouseClick(self, x, y, button, pressed):
        if not self.cache["recording"]: return
        if pressed:
            _time = time() - self.start_time
            log_dict = generateLogLine(_time, "Mouse", "press", [x,y,button], kwargs={})
            self.cache["mouse_pressed"] = True
        else:
            _time = time() - self.start_time
            log_dict = generateLogLine(_time, "Mouse", "release", [x,y,button], kwargs={})
            self.cache["mouse_pressed"] = False
        self.events.append(log_dict)
    
    def onMouseScroll(self, x, y, dx, dy):
        if not self.cache["recording"]: return
        _time = time() - self.start_time
        log_dict = generateLogLine(_time, "Mouse", "scroll", [x,y,dx, dy], kwargs={})
        self.events.append(log_dict)
    
    def onKeyboardPress(self, key):
        if not self.cache["recording"]: return
        _time = time() - self.start_time
        if key==self.STOP_KEY:
            self.stopAndLog()
            return
        log_dict = generateLogLine(_time, "Keyboard", "press", [key], kwargs={})
        self.events.append(log_dict)

    def onKeyboardRelease(self, key):
        if not self.cache["recording"]: return
        _time = time() - self.start_time
        log_dict = generateLogLine(_time, "Keyboard", "release", [key], kwargs={})
        self.events.append(log_dict)

    def start(self):
        for i in list(range(int(getConf("record_after"))))[::-1]:
            print(i+1)
            sleep(1)
        self.events = []
        self.start_time = time()
        self.start_time_str = ctime(self.start_time)
        # start event
        log_dict = generateLogLine(0, "Virtual", "hold")
        self.events.append(log_dict)

        self.mouse_listener = pynput.mouse.Listener(
            on_move = self.onMouseMove,
            on_click = self.onMouseClick,
            on_scroll = self.onMouseScroll
        )
        self.keyboard_listener = pynput.keyboard.Listener(
            on_press = self.onKeyboardPress,
            on_release = self.onKeyboardRelease
        )
        print("Start recording")
        print("Press {} to stop.".format(self.STOP_KEY))
        def mouseListen():
            with self.mouse_listener as mouse_listener:
                try:
                    mouse_listener.join()
                except:
                    pass
        def keyboardListen():
            with self.keyboard_listener as keyboard_listener:
                try:
                    keyboard_listener.join()
                except:
                    pass
        if not self.cache["thread_started"]:
            self.threads.append(threading.Thread(target=mouseListen, daemon=True))
            self.threads.append(threading.Thread(target=keyboardListen, daemon=True))
            [i.start() for i in self.threads]
            self.cache["thread_started"] = True
        self.cache["recording"] = True
        # self.mouse_listener.start()
        # self.keyboard_listener.start()

    def stop(self):
        print("Stop recording")
        self.cache["recording"] = False
        # self.mouse_listener.stop()
        # self.keyboard_listener.stop()       # Will somehow lead to bug (in Ubuntu?)
        _time = time() - self.start_time
        # Finish event
        log_dict = generateLogLine(_time, "Virtual", "hold")
        self.events.append(log_dict)
        record =  {
            "start_time_str": self.start_time_str,
            "events": self.events
        }
        return record
    
    def writeLog(self, record: dict):
        print("Writing log...")
        with open(self.record_file, "wb") as fp:
            b_string = pickle.dumps(record, 3)
            fp.write(b_string)
        print("Recording write to: ", self.record_file)
    
    def stopAndLog(self):
        record = self.stop()
        self.writeLog(record)
    
    def loadLog(self):
        with open(self.record_file, "rb") as fp:
            b_string = fp.read()
            record: dict = pickle.loads(b_string)
        for k, v in record.items():
            self.__setattr__(k, v)
