from ..utils import CATEGORY, any
from PythonSed import Sed, SedException
import io

sed = Sed()

class SedOnString:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "script_string": ("STRING", {"default": "'s/old/new/g'"}),
            },
            "optional": {
                "STRING": (any, ),
            }
        }

    RETURN_TYPES = ("STRING", )
    FUNCTION = "do_stringsed"
    CATEGORY = CATEGORY.MAIN.value + "/Advanced/Tools"

    def do_stringsed(self, script_string, STRING=None):

        sed.load_string(script_string)
        trick_sed = io.StringIO(STRING)
        modified_STRING = sed.apply(trick_sed)

        return(modified_STRING, )



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