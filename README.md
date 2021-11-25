# KeyMouseRecorder
A screen recorder (based on [pynput](https://pypi.org/project/pynput/)), record keyboard and mouse events.

## Installation
```bash
python setup.py install
```

## Usage
```bash
recordKM            # Open GUI
recordKM --help     # For help
```

**help**:
```
usage: . [-h] [-r] [-p] [-f FILE_PATH]  

Screen recorder, run without argument to start GUI. | Author: Mengxun Li (mengxunli@whu.edu.cn)  

optional arguments:  
-h, --help            show this help message and exit  
-r, --record          Start recording directly without GUI.  
-p, --play            Start playing directly without GUI.  
-f FILE_PATH, --file_path FILE_PATH  
                       Set log file path.
```
The configuration file is at `<package_path>/recKeyMouse/conf.json`