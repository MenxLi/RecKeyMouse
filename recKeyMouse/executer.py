import time, threading

from recKeyMouse.confReader import getConf
from .logger import ActionLogger
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

class KeyboardExecuter(DeviceExecuter):
    def __init__(self) -> None:
        self.keyboard = K_Controller()
    
    def press(self, key):
        self.keyboard.press(key)

    def release(self, key):
        self.keyboard.release(key)

class Executer():
    def __init__(self, file) -> None:
        self.logger = ActionLogger(file)
        self.logger.loadLog()
        self.m_executer = MouseExecuter()
        self.k_executer = KeyboardExecuter()
    
    def run(self, replay_times = 1): 
        for i in range(replay_times):
            print("=================================")
            print("replaying... time {}/{}:".format(i+1, replay_times))
            m_thread = threading.Thread(target=self._runEventsThread, args = [self.m_executer, self.logger.mouse_events])
            k_thread = threading.Thread(target=self._runEventsThread, args = [self.k_executer, self.logger.keyboard_events])
            m_thread.start()
            k_thread.start()
            m_thread.join()
            k_thread.join()
            if replay_times > 1:
                time.sleep(getConf("rest_between_replay"))
        print("Finished replay.")
    
    def _runEventsThread(self, executer: DeviceExecuter, events: dict):
        prev_time = 0
        for e in events:
            print(e)
            exec_time = e["time"]
            time.sleep(exec_time - prev_time)
            prev_time = exec_time
            executer.runMethod(e["method"], *e["args"], **e["kwargs"])


            
    