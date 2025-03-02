'''
    !DISCLAIMER! I'm very new to programming and I've been heavily inspired by following.
https://github.com/crystian/ComfyUI-Crystools
  Many thanks goes to these awesome developers!
'''
from .utils import any, BOOLEAN, STRING, CATEGORY

class BooleanToPipe:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_1": BOOLEAN,
                "boolean_2": BOOLEAN,
                "boolean_3": BOOLEAN,
                "boolean_4": BOOLEAN,
            }
        }

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value
    RETURN_TYPES = ("BoolPipe",)

    FUNCTION = "execute"

    def execute(self, boolean_1=True, boolean_2=True, boolean_3=True, boolean_4=True):
        # Create a list to hold the boolean values
        BoolPipeMod = []

        # Append the boolean values directly
        BoolPipeMod.append(boolean_1)
        BoolPipeMod.append(boolean_2)
        BoolPipeMod.append(boolean_3)
        BoolPipeMod.append(boolean_4)

        # Return the list as separate boolean outputs
        return (BoolPipeMod,)

class BooleanFromPipe:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "BoolPipe": (any,),
            },
            "optional": {
            }
        }

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value
    RETURN_TYPES = ("BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN",)
    RETURN_NAMES = ("boolean_1", "boolean_2", "boolean_3", "boolean_4",)

    FUNCTION = "execute"

    def execute(self, BoolPipe=None, ):
        boolean_1, boolean_2, boolean_3, boolean_4, = BoolPipe
        return boolean_1, boolean_2, boolean_3, boolean_4

