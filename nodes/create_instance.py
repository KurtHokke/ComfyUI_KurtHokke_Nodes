from custom_nodes.ComfyUI_KurtHokke_Nodes.utils import CATEGORY, anytype, prefix
from custom_nodes.ComfyUI_KurtHokke_Nodes.helpers import check_string, find_and_import_class
from custom_nodes.ComfyUI_KurtHokke_Nodes.loggers import get_logger
from comfy.comfy_types import IO, InputTypeDict
import sys
import re

logger, decoDebug = get_logger("all")

@decoDebug
class CreateInstance:
    def __init__(self):
        self.instance = "None"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "x_eq": ("STRING", {"default": "", "defaultInput": False}),
            }
        }
    RETURN_TYPES = (anytype, )
    FUNCTION = "create_instance"
    CATEGORY = CATEGORY.MAIN.value

    def done(self, y):
        xinstance = self.instance
        return {
            "ui": {
                "string": [y, ]
            },
            "result": (xinstance,)
        }
    def create_instance(self, x_eq):
        regex = r"^(\w+)\(\(([\w\s,]*)\)\)$"
        match = re.match(regex, x_eq)
        instancename = x_eq
        #instancename = re.sub(r'\(.*$', '', x_eq)
        instance = find_and_import_class(instancename)
        if instance is not None:
            self.instance = instance
            return self.done(f"Instance of {instancename} created")
        else:
            return self.done(f"No class named '{instancename}' found")
        # Check if the string matches the pattern <ClassName>((arg1, arg2, ...))
        if match:
            class_name = match.group(1)  # Extract class name
            args = match.group(2)  # Extract arguments as a comma-separated string

            # Split arguments if not empty, otherwise, use an empty tuple
            args = tuple(arg.strip() for arg in args.split(",")) if args else ()

            # Search for the class in globals
            for cls_name, cls_obj in globals().items():
                # Check if the class name matches and is a valid class
                if cls_name == class_name and isinstance(cls_obj, type):
                    try:
                        # Dynamically create an instance of the class with arguments
                        self.instance = cls_obj(*args)
                        return self.done(f"Instance of {cls_name} created with arguments {args}")
                    except TypeError as e:
                        # Handle argument mismatch issues
                        return self.done(f"Failed to create instance of '{cls_name}': {str(e)}")

            # If class not found
            return self.done(f"No class named '{class_name}' found")

        # If there is no argument pattern, fallback to exact match logic
        for cls_name, cls_obj in globals().items():
            if cls_name == x_eq and isinstance(cls_obj, type):
                self.instance = cls_obj()
                return self.done(f"Instance of {cls_name} created")

        # If no class matches
        return self.done(f"No class or valid format found for '{x_eq}'")

NODE_CLASS_MAPPINGS = {
    "CreateInstance": CreateInstance,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "CreateInstance": prefix + "CreateInstance",
}