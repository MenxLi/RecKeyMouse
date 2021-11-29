from pynput import mouse, keyboard

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
            return arg.strip("'")
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
def generateLogLine(time: float, device: str, method: str, args: list = [], kwargs: dict = {}) -> Logline:
    log_dict = {
        "time": time,
        "device": device,
        "method": method,
        "args": args,
        "kwargs": kwargs
    }
    return Logline(log_dict)