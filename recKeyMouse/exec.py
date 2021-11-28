from PyQt5.QtWidgets import QApplication
import sys, argparse, time

from recKeyMouse.version import VERSION
from .recorder import RecorderWindow
from .logger import ActionLogger
from .executer import Executer
from .confReader import writeConf, getConf, generateDefaultConf, CONF_PATH
from .eventEditor import EventEditor
from .utils import openFile

def startGUI(saving_path: str = None):
    app = QApplication(sys.argv)
    gui = RecorderWindow(saving_path = saving_path)
    sys.exit(app.exec_())

def startEditorGUI(saving_path: str = None):
    app = QApplication(sys.argv)
    editor = EventEditor()
    editor.loadEventFile(saving_path)
    sys.exit(app.exec_())

def main():
    parser = argparse.ArgumentParser(
        description="Screen recorder, run without argument to start GUI. | Author: Mengxun Li (mengxunli@whu.edu.cn)"
    )
    parser.add_argument(
        "-r", "--record", action="store_true", default=False, 
        help = "Start recording directly without GUI."
    )
    parser.add_argument(
        "-p", "--play", action="store_true", 
        help = "Start playing directly without GUI."
    )
    parser.add_argument(
        "-f", "--file_path", default=getConf("log_path"), 
        help = "Set recording file path."
    )
    parser.add_argument(
        "-e", "--edit", action="store_true", default=False, 
        help = "Edit events."
    )
    parser.add_argument(
        "--configure", action="store_true", default=False, 
        help = "Open configuration json file."
    )
    parser.add_argument(
        "--init_configure", action="store_true", default=False, 
        help = "Generate default configuration file."
    )
    parser.add_argument(
        "--version", action="store_true", default=False, 
        help = "Show version."
    )

    args = parser.parse_args()

    if args.init_configure:
        generateDefaultConf()
        return
    
    if args.configure:
        openFile(CONF_PATH)
        return
    
    if args.version:
        print(VERSION)
        return

    if args.record:
        logger = ActionLogger(args.file_path)
        logger.start()
        while(True):
            if not logger.cache["recording"] and logger.cache["thread_started"]:
                time.sleep(1)   # for writing record file
                break
    elif args.play:
        executer = Executer(args.file_path)
        executer.run(getConf("replay_times"))
    elif args.edit:
        startEditorGUI(args.file_path)
    else: 
        startGUI(args.file_path)

if __name__=="__main__":
    main()
