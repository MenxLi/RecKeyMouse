# KeyMouseRecorder
A screen recorder (based on [pynput](https://pypi.org/project/pynput/)), record keyboard and mouse events.

## Installation
```bash
pip install .
```

## Usage
```bash
reckm             # Open GUI
reckm -e          # Open event editor GUI
reckm -r          # Start recording (no GUI)
reckm -p          # Start replaying (no GUI)
reckm --help      # For help
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
  -e, --edit            Edit events.
  --configure           Open configuration json file.
  --init_configure      Generate default configuration file.
  --version             Show version.
```

## API
```python
from recKeyMouse.api import ActionLogger, Executer, startGUI, startEditorGUI

recording_file = "recording/file/path" 

# Recording
logger = ActionLogger(recording_file)
logger.start()    # Press ActionLogger.STOP_KEY to stop recording

# Execute
executer = Executer(recording_file)
executer.run()    # Press ActionLogger.STOP_KEY to stop replaying

# Start GUI
startGUI(recording_file)

# Start editor GUI
startEditorGUI(recording_file)
```

## Settings
Run `recordKM --configure` to edit with default json editor.

## Future directions
- [x] Event editor
- [ ] Configuration editor