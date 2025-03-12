from ..utils import CATEGORY, any

class debug_object:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "object": (any, ),
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "debug"
    CATEGORY = CATEGORY.MAIN.value + ""

    def debug(self, object,):
        delimiter = " "
        obj_str = delimiter.join(object)
        string = f"DEBUG: {obj_str}"
        return (string,)
