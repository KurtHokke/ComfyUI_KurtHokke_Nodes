from ..utils import CATEGORY, any
from ..core import DataHandler
from ..helpers import ConfigManager, restricted_import, original_import
from ..loggers import get_logger
import builtins
import black
import json
import re

logger, log_all = get_logger("log_all")


debugany_config = ConfigManager("debugany.config")

DEBUGANY_BASEOPTS = ["None", "Save script", "Call Attributes"]
DEBUGANY_OPTS = debugany_config.generate_list(DEBUGANY_BASEOPTS, "debugany.config")

@log_all
class DebugAny2:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                #"presets": (DEBUGANY_OPTS, ),
                "params": ("STRING", {"multiline": False, "default": "", "defaultInput": False}),
            },
            "optional": {
                "a": (any, {"forceInput": True}),
                #"b": (any, {"forceInput": True}),
                #"script": ("STRING", {"forceInput": True}),
            }
        }
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    CATEGORY = CATEGORY.MAIN.value
    FUNCTION = "display_x"

    def done(self, x):
        return {
            "ui": {
                "string": [x, ]
            },
            "result": (x,)
        }
    def display_x(self, params="", a=None) -> str:
        if params == "" and a is None:
            return self.done(x="")
        elif params == "" and a is not None:
            code = f"result = {a}"
        else:
            code = f"result = {params}"
        context = {"a": a}
        exec(code, globals(), context)
        return self.done(x=str(context["result"]))
