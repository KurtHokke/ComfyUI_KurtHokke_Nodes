from ..utils import CATEGORY, any, logger


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
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

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
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

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
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

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
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

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
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

    def stringify(self, string):
        return (string, )

class Node_RandomRange:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "min": ("FLOAT", {"default": 0.00, "min": -9999999999.00, "max": 9999999999.00, "step": 0.001}),
                "max": ("FLOAT", {"default": 10.00, "min": -9999999999.00, "max": 9999999999.00, "step": 0.001}),
            }
        }
    RETURN_TYPES = ("INT", "FLOAT")
    FUNCTION = "randomrange"
    OUTPUT_NODE = True
    IS_CHANGED = True
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

    def randomrange(self, min, max):
        import random
        random_float = random.uniform(min, max)
        random_int = int(random_float)
        return random_int, random_float

class CompareTorch:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "a": (any , ),
                "b": (any , ),
            }
        }
    RETURN_TYPES = (any, any, )
    RETURN_NAMES = ("boolean", "*", )
    FUNCTION = "compare"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

    def unlist(self, nested):
        if not isinstance(nested, (list, tuple)):
            return [nested]  # Base case: If not iterable, wrap in a list.

        flattened = []
        for item in nested:
            flattened.extend(self.unlist(item))  # Recursively flatten the structure.
        return flattened

    def compare(self, a, b):
        import torch
        import logging
        logger = logging.getLogger()
        for handler in logging.getLogger().handlers:
            print(handler)
            print(handler)
            print(handler)
            print(handler)
            print(handler)

        logger.info(f"{a}, {b}")
        if isinstance(a, list):
            logger.info(f"unlisting {a}")
            a = self.unlist(a)
        if isinstance(b, list):
            logger.info(f"unlisting {b}")
            b = self.unlist(b)
        logger.info(f"type(a) == {type(a)}\ntype(b) == {type(b)}")
        if not isinstance(a, torch.Tensor) or not isinstance(b, torch.Tensor):
            exeptionstr = f"type(a) = {type(a)}, type(b) = {type(b)}\nCannot compare as both are not tensors"
            return (exeptionstr, exeptionstr)
        elif torch.equal(a, b):
            return (True, f"a == b ==\\\n{a}")
        else:
            # Find element-wise differences if tensors are not equal
            diff_indices = (a != b).nonzero(as_tuple=True)
            differences = [f"At index {index}: a = {val1}, b = {val2}"
                           for index, val1, val2 in zip(diff_indices[0], a[diff_indices], b[diff_indices])]
            return "\n".join(differences) or "Tensors have the same shape and elements."
