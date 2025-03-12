from ..utils import CATEGORY
import re

class re_sub_str:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "script_str": ("STRING", {"default": "\s+\\n$", "multiline": False}),
                "script_rpl": ("STRING", {"default": ", ", "multiline": False}),
            },
            "optional": {
                "string": ("STRING", {"default": '', "multiline": True, "defaultInput": True}),
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "re_do_sub"
    CATEGORY = CATEGORY.MAIN.value + "/Tools"

    def re_do_sub(self, string, script_str, script_rpl):
        out = re.sub(script_str, script_rpl, string)
        return (out,)
