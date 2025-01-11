import os, json, platformdirs
from .version import VERSION

ICON_PATH = os.path.join(os.path.dirname(__file__), "icons")
if os.environ.get("RECKM_DATA", None) is not None:
    DATA_DIR = os.environ.get("RECKM_DATA")
    if not os.path.exists(DATA_DIR): os.mkdir(DATA_DIR)
else:
    DATA_DIR = platformdirs.user_data_dir("reckm", appauthor="li_mengxun", ensure_exists=True, version=VERSION)
CONF_PATH = os.path.join(DATA_DIR, "rkm_conf.json")

def getConf(keyword):
    if not os.path.exists(CONF_PATH):
        generateDefaultConf()
    with open(CONF_PATH,'r') as fp:
        _conf = json.load(fp)[keyword]
    return _conf

def writeConf(keyword, value):
    with open(CONF_PATH) as fp:
        conf = json.load(fp)
    conf[keyword] = value
    with open(CONF_PATH) as fp:
        conf = json.dump(conf, fp)

def generateDefaultConf():
    default_log_path = os.path.join(DATA_DIR, "record.pkl")
    conf = {
        "log_path": os.path.abspath(default_log_path),
        "record_after":3,
        "record_mouse_motion": False,
        "replay_times": 1, 
        "rest_between_replay": 1
    }
    with open(CONF_PATH, "w") as fp:
        json.dump(conf, fp, indent=2)