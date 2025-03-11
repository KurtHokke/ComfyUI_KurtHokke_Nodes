from ..utils import CATEGORY

class Node_BOOL:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "value": ("BOOLEAN", {"default": True}),
        },
        }
    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("value",)
    FUNCTION = "get_value"
    CATEGORY = CATEGORY.MAIN.value + "/Utils"

    def get_value(self, value):
        return (value,)

class Node_INT:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "value": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
        },
        }
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("value",)
    FUNCTION = "get_value"
    CATEGORY = CATEGORY.MAIN.value + "/Utils"

    def get_value(self, value):
        return (value,)

class Node_Float:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "value": ("FLOAT", {"default": 0.0, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff, "step": 0.00001}),
        },
        }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("value",)
    FUNCTION = "get_value"
    CATEGORY = CATEGORY.MAIN.value + "/Utils"

    def get_value(self, value):
        return (value,)

class Node_String:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "_": ("STRING", {"default": '', "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "passtring"
    CATEGORY = CATEGORY.MAIN.value + "/Utils"

    def passtring(self, _):
        string = _
        return (string, )

class Node_StringMultiline:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"default": "", "multiline": True}),
            }
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "stringify"
    CATEGORY = CATEGORY.MAIN.value + "/Utils"

    def stringify(self, string):
        return (string, )