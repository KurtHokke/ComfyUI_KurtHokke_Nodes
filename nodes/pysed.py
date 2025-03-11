from ..utils import CATEGORY
from ..packages.PythonSed import Sed, SedException
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
    CATEGORY = CATEGORY.MAIN.value + "/Tools"

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



'''
# Load a script from a string
my_script_string = """
s/old/new/g
"""
sed.load_string(my_script_string)

# Alternatively, load a script from a file
# with open('my_script.sed', 'r') as f:
#     sed.load_script(f)

# Example input string
input_string = "This is the old string."
input_file_like = io.StringIO(input_string)

# Apply the sed script to the input string
output_string = sed.apply(input_file_like)

print(output_string)  # Output: This is the new string.
'''