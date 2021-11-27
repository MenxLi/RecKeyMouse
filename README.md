# KeyMouseRecorder
A screen recorder (based on [pynput](https://pypi.org/project/pynput/)), record keyboard and mouse events.

## Installation
```bash
python setup.py install
```

## Usage
```bash
recordKM            # Open GUI
recordKM -r         # Record (no GUI)
recordKM -p         # Replay (no GUI)
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
                        Set recording file path.
  --configure           Open configuration json file.
  --init_configure      Generate default configuration file.
```

## API
```python
from recKeyMouse import ActionLogger, Executer, startGUI

recording_file = "<recording file path>" 

# Recording
logger = ActionLogger(recording_file)
logger.start()    # Press logger.STOP_KEY to stop recording

# Execute
executer = Executer(recording_file)
executer.run()

# Start GUI
startGUI()
```

## Settings
The configuration file is at `<package_path>/recKeyMouse/conf.json`  
Run `recordKM --configure` to edit with default json editor.

## Future directions
- [ ] Event editor
- [ ] Configuration editor