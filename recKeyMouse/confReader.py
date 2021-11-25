import os, json

def getConf(keyword):
    curr_dir = os.path.dirname(__file__)
    with open(os.path.join(curr_dir, "conf.json"),'r') as fp:
        _conf = json.load(fp)[keyword]
    return _conf

def writeConf(keyword, value):
    curr_dir = os.path.dirname(__file__)
    with open(os.path.join(curr_dir, "conf.json"),'r') as fp:
        conf = json.load(fp)
    conf[keyword] = value
    with open(os.path.join(curr_dir, "conf.json"),'w') as fp:
        conf = json.dump(conf, fp)