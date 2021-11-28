from io import TextIOWrapper
from time import ctime, time, sleep
import pickle, threading, os

import pynput
from pynput import mouse
from pynput import keyboard
from pynput.mouse import Controller as M_Controller
from pynput.mouse import Button as M_Button
from .confReader import getConf

class LoglineUtils():
    @staticmethod
    def _reverseArgs(args_str: str):
        if args_str == "":
            return []
        args_str = args_str.replace(" ", "")
        args_str = args_str.split(",")
        return [LoglineUtils.__auto_type(a) for a in args_str]

    @staticmethod
    def _reverseKwargs(kwargs_str: str):
        if kwargs_str == "":
            return {}
        kwargs_str = kwargs_str.replace(" ", "")
        kwargs_str = kwargs_str.split(",")
        raise NotImplementedError

    @staticmethod
    def __auto_type(arg: str):
        if arg.startswith("Button."):
            if arg == "Button.right":
                return mouse.Button.right
            if arg == "Button.left":
                return mouse.Button.left
            if arg == "Button.middle":
                return mouse.Button.middle
        if arg.startswith("Key."):
            arg = arg[4:]
            return getattr(keyboard.Key, arg)
        if arg.startswith("'"):
            # General Key
            return arg
        if arg.isalpha():
            return str(arg)
        if "." in arg:
            return float(arg)
        if arg.isnumeric():
            return int(arg)

class Logline(dict, LoglineUtils):
    INDEX_FUNC = [ 
        ["time", lambda x: str(x["time"])],
        ["device", lambda x: x["device"]],
        ["method", lambda x: x["method"]],
        ["args", lambda x: ", ".join([str(i) for i in x["args"]])],
        ["kwargs", lambda x: ", ".join(["{}: {}".format(k, v) for k, v in x["kwargs"].items()])]
     ]
    INDEX_FUNC_DICT = dict()
    for i in INDEX_FUNC:
        INDEX_FUNC_DICT[i[0]] = i[1]
    REVERSE_FUNC = [
        ["time", lambda x: float(x)],
        ["device", lambda x: x],
        ["method", lambda x: x],
        ["args", lambda x: LoglineUtils._reverseArgs(x)],
        ["kwargs", lambda x: LoglineUtils._reverseKwargs(x)]
     ]
    REVERSE_FUNC_DICT = dict()
    for i in REVERSE_FUNC:
        REVERSE_FUNC_DICT[i[0]] = i[1]
    

    def __init__(self, log_dict: dict):
        super().__init__(log_dict)
    
    def getStrItemByIndex(self, idx: int):
        return self.INDEX_FUNC[idx][1](self)
    
    def __repr__(self) -> str:
        time_str = str(round(self["time"],2)) + "s"
        device_str = self["device"]
        method_str = self["method"]
        args_str = ", ".join([str(arg) for arg in self["args"]])
        kwargs_str = ""
        for k, v in self["kwargs"].items():
            kwargs_str += f"{k} = {v}"
        out = f"{time_str}: {device_str}-{method_str}({args_str}, {kwargs_str})"
        return out
    
    __str__ = __repr__

class ParseLog():
    """
    Parse a single line of the log
    """
    @staticmethod
    def generateLogLine(time: float, device: str, method: str, args: list = [], kwargs: dict = {}) -> Logline:
        log_dict = {
            "time": time,
            "device": device,
            "method": method,
            "args": args,
            "kwargs": kwargs
        }
        return Logline(log_dict)

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
        log_dict = ParseLog.generateLogLine(_time, "Mouse", "setPos", [x,y], kwargs={})
        self.events.append(log_dict)

    def onMouseClick(self, x, y, button, pressed):
        if not self.cache["recording"]: return
        if pressed:
            _time = time() - self.start_time
            log_dict = ParseLog.generateLogLine(_time, "Mouse", "press", [x,y,button], kwargs={})
            self.cache["mouse_pressed"] = True
        else:
            _time = time() - self.start_time
            log_dict = ParseLog.generateLogLine(_time, "Mouse", "release", [x,y,button], kwargs={})
            self.cache["mouse_pressed"] = False
        self.events.append(log_dict)
    
    def onMouseScroll(self, x, y, dx, dy):
        if not self.cache["recording"]: return
        _time = time() - self.start_time
        log_dict = ParseLog.generateLogLine(_time, "Mouse", "scroll", [x,y,dx, dy], kwargs={})
        self.events.append(log_dict)
    
    def onKeyboardPress(self, key):
        if not self.cache["recording"]: return
        _time = time() - self.start_time
        if key==self.STOP_KEY:
            self.stopAndLog()
            return
        log_dict = ParseLog.generateLogLine(_time, "Keyboard", "press", [key], kwargs={})
        self.events.append(log_dict)

    def onKeyboardRelease(self, key):
        if not self.cache["recording"]: return
        _time = time() - self.start_time
        log_dict = ParseLog.generateLogLine(_time, "Keyboard", "release", [key], kwargs={})
        self.events.append(log_dict)

    def start(self):
        for i in list(range(int(getConf("record_after"))))[::-1]:
            print(i+1)
            sleep(1)
        self.events = []
        self.start_time = time()
        self.start_time_str = ctime(self.start_time)
        # start event
        log_dict = ParseLog.generateLogLine(0, "Virtual", "hold")
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
        log_dict = ParseLog.generateLogLine(_time, "Virtual", "hold")
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
