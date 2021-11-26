import os, json
curr_path = os.path.dirname(__file__)
CONF_PATH = os.path.join(curr_path, "conf.json")

def getConf(keyword):
    curr_path = os.path.dirname(__file__)
    conf_path = os.path.join(curr_path, "conf.json")
    if not os.path.exists(conf_path):
        generateDefaultConf()
    with open(conf_path,'r') as fp:
        _conf = json.load(fp)[keyword]
    return _conf

def writeConf(keyword, value):
    curr_dir = os.path.dirname(__file__)
    with open(os.path.join(curr_dir, "conf.json"),'r') as fp:
        conf = json.load(fp)
    conf[keyword] = value
    with open(os.path.join(curr_dir, "conf.json"),'w') as fp:
        conf = json.dump(conf, fp)

def generateDefaultConf():
    curr_path = os.path.dirname(__file__)
    conf_path = os.path.join(curr_path, "conf.json")
    default_log_path = os.path.join(curr_path, "record.pkl")
    conf = {
        "log_path": os.path.abspath(default_log_path),
        "record_after":3,
        "record_mouse_motion": False,
        "replay_times": 1, 
        "rest_between_replay": 1
    }
    with open(conf_path, "w") as fp:
        json.dump(conf, fp, indent=2)