from ..utils import CATEGORY
from ..packages.PythonSed import Sed, SedException
import io

sed = Sed()

class SedOnString:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "script_string": ("STRING", {"default": 's/old/new/g', "multiline": False}),
            },
            "optional": {
                "STRING": ("STRING", {"default": '', "multiline": False, "defaultInput": True}),
            }
        }

    RETURN_TYPES = ("STRING", )
    FUNCTION = "do_stringsed"
    CATEGORY = CATEGORY.MAIN.value + "/Advanced/Tools"

    def do_stringsed(self, script_string, STRING=None):

        if STRING is None:
            return ("", )

        try:
            sed.load_string(script_string) 
        except SedException as e:
            print(f"Error loading sed script: {e}")
            return ("", )

        trick_sed = io.StringIO(STRING)

        try:
            modified_list = sed.apply(trick_sed)
            delimiter = " "
            modified_str = delimiter.join(modified_list)
            new_string = []
            for line in io.StringIO(modified_str):
                if not line.strip().startswith("\n"):
                    line = line.replace("\n", '')
                new_string.append(line)
            new_string = "\n".join(new_string)
            return (new_string, )
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