from khn.utils import CATEGORY, prefix
from khn.packages.PythonSed import Sed, SedException
import io
import re

sed = Sed()

class SedOnString:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "script_str": ("STRING", {"default": 's/old/new/', "multiline": False}),
            },
            "optional": {
                "STRING": ("STRING", {"default": '', "multiline": True, "defaultInput": True}),
            }
        }

    RETURN_TYPES = ("STRING", )
    FUNCTION = "do_stringsed"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.TOOLS.value

    def do_stringsed(self, script_str, STRING=None):

        if STRING is None:
            return ("", )

        try:
            sed.load_string(script_str)
        except SedException as e:
            print(f"Error loading sed script: {e}")
            return ("", )

        trick_sed = io.StringIO(STRING)

        try:
            modified_list = sed.apply(trick_sed)
            delimiter = " "
            modified_str = delimiter.join(modified_list)
            stripped_str = re.sub(r'\n\s', '\n', modified_str)
            complete_str = re.sub(r'\n$', '', stripped_str)
            return (complete_str, )
        except SedException as e:
            print(f"Error applying sed script: {e}")
            return ("", )  # Return an empty string on error


NODE_CLASS_MAPPINGS = {
    "SedOnString": SedOnString,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "SedOnString": prefix + "SedOnString",
}