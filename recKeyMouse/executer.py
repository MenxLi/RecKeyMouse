import time, threading
from typing import Callable, List, Union

from pynput import keyboard

from recKeyMouse.confReader import getConf
from .logger import ActionLogger, Logline
import pickle
import pynput
from pynput.mouse import Controller as M_Controller
from pynput.mouse import Button as M_Button
from pynput.keyboard import Controller as K_Controller

class DeviceExecuter():
    def hold(self):
        # do nothing for now, as a place-holder
        return
    def runMethod(self, method, *args, **kwargs):
        self.__getattribute__(method)(*args, **kwargs)

class VirtualExecuter(DeviceExecuter):

    def __init__(self) -> None:
        super().__init__()
        self.__callback_dict = {
            "default": lambda : None,
        }

    def setCallback(self, flag: str, func: Callable):
        self.__callback_dict[flag] = func

    def callback(self, flag = "default"):
        self.__callback_dict[flag]()

class MouseExecuter(DeviceExecuter):
    def __init__(self) -> None:
        self.mouse = M_Controller()

    def setPos(self, x, y):
        self.mouse.position = (x,y)

    def press(self, x, y, button):
        self.setPos(x, y)
        self.mouse.press(button)

    def release(self, x, y, button):
        self.setPos(x, y)
        self.mouse.release(button)
    
    def scroll(self, x, y, dx, dy):
        self.setPos(x, y)
        self.mouse.scroll(dx, dy)
    
    def click(self, x, y, button):
        self.setPos(x, y)
        self.mouse.press(button)
        self.mouse.release(button)

class KeyboardExecuter(DeviceExecuter):
    def __init__(self) -> None:
        self.keyboard = K_Controller()
    
    def press(self, key):
        self.keyboard.press(key)

    def release(self, key):
        self.keyboard.release(key)

    def click(self, key):
        self.press(key)
        self.release(key)
    
    def input(self, string: str):
        self.keyboard.type(string)

class Executer():
    def __init__(self, file: Union[str, None] = None) -> None:
        if file:
            self.setFile(file)
        self.m_executer = MouseExecuter()
        self.k_executer = KeyboardExecuter()
        self.v_executer = VirtualExecuter()
        self.executers = {
            "Mouse": self.m_executer,
            "Keyboard": self.k_executer,
            "Virtual": self.v_executer
        }
        self.k_listener =  keyboard.Listener(on_release = self.stopOnRelease)
        self.__allow_run = True
    
    def setFile(self, file: str) -> None:
        self.logger = ActionLogger(file)
        self.logger.loadLog()
    
    def stopOnRelease(self, key):
        if key == ActionLogger.STOP_KEY:
            self.__allow_run = False
    
    def run(self, replay_times = 1, events: Union[List[Logline], None] = None): 
        if events is None:
            if hasattr(self, "logger"):
                events = self.logger.events
            else:
                raise Exception("Failed to run because events not set, use Executer.setFile or run(events) to set events.")
        print("+++++++++++++++++++++++++++++++++")
        print("Start replaying...")
        print("Press {} to stop replay.".format(ActionLogger.STOP_KEY))
        for i in range(replay_times):
            print("=================================")
            print("replaying... time {}/{}:".format(i+1, replay_times))
            thread = threading.Thread(target=self._runEventsThread, args = [events])
            thread.start()
            self.k_listener.start()
            thread.join()
            if replay_times > 1:
                time.sleep(getConf("rest_between_replay"))
        print("Finished replay.")
    
    def _runEventsThread(self, events: List[Logline]):
        prev_time = 0
        for e in events:
            if not self.__allow_run:
                self.k_listener.stop()
                self.k_listener.join()
                print("**Terminated**")
                break
            print(e)
            exec_time = e["time"]
            time.sleep(exec_time - prev_time)
            prev_time = exec_time
            executer: DeviceExecuter = self.executers[e["device"]]
            executer.runMethod(e["method"], *e["args"], **e["kwargs"])
        self.__allow_run = True


            
    