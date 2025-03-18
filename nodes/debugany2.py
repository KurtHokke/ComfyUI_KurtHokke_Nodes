from ..utils import CATEGORY, anytype
from ..helpers import ConfigManager
from ..loggers import get_logger
from comfy.comfy_types import IO, InputTypeDict

logger, log_all = get_logger("log_all")

debugany_config = ConfigManager("debugany.config")

DEBUGANY_BASEOPTS = ["None", "Save script", "Call Attributes"]
DEBUGANY_OPTS = debugany_config.generate_list(DEBUGANY_BASEOPTS, "debugany.config")

@log_all
class DebugAny3:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "I1": (anytype, {"forceInput": True}),
                "I2": (anytype, {"forceInput": True}),
                "I3": (anytype, {"forceInput": True}),
                "I4": (anytype, {"forceInput": True}),
                "I5": (anytype, {"forceInput": True}),
                "I6": (anytype, {"forceInput": True}),
                "I7": (anytype, {"forceInput": True}),
                "I8": (anytype, {"forceInput": True}),
                "O1_eq": ("STRING", {"multiline": False, "default": "", "defaultInput": False}),
                "O2_eq": ("STRING", {"multiline": False, "default": "", "defaultInput": False}),
                "O3_eq": ("STRING", {"multiline": False, "default": "", "defaultInput": False}),
                "O4_eq": ("STRING", {"multiline": False, "default": "", "defaultInput": False}),
                "O5_eq": ("STRING", {"multiline": False, "default": "", "defaultInput": False}),
                "O6_eq": ("STRING", {"multiline": False, "default": "", "defaultInput": False}),
                "O7_eq": ("STRING", {"multiline": False, "default": "", "defaultInput": False}),
                "O8_eq": ("STRING", {"multiline": False, "default": "", "defaultInput": False}),
            }
        }
    RETURN_TYPES = (anytype, anytype, anytype, anytype, anytype, anytype, anytype, anytype, )
    RETURN_NAMES = ("O1", "O2", "O3", "O4", "O5", "O6", "O7", "O8", )
    OUTPUT_NODE = True
    CATEGORY = CATEGORY.MAIN.value
    FUNCTION = "display_x"

    def done(self, x):
        if len(str(x)) > 5000:
            x = str(x)[:5000] + "...Too long string"
        return {
            "ui": {
                "string": [x, ]
            },
            "result": (x,)
        }
    def display_x(self, **kwargs: any):
        #if params == "" and all(arg is None for arg in args):
            #return self.done(x="")

        logger.debug(f"###\n{kwargs}\n###")
        logger.debug(f"###\nkwargs: {kwargs}\n###")

        #context = {key: value for key, value in kwargs.items() if value is not None}
        input_data = {}  # Dictionary to store data for inputs

        for i in range(1, 9):  # Handle O1_eq to O8_eq with corresponding I1 to I8
            o_key = f"O{i}_eq"  # Key for the output transformation logic
            i_key = f"I{i}"  # Key for the corresponding input

            if o_key in kwargs and kwargs[o_key]:  # Check if O\d_eq exists and is not empty
                try:
                    # Get the input value
                    input_value = kwargs.get(i_key, None)

                    # Dynamically evaluate the transformation in O\d_eq
                    transformation = kwargs[o_key]
                    transformed_value = eval(transformation, {}, {"I": input_value})

                    # Save the transformed value
                    input_data[i_key] = transformed_value
                except Exception as e:
                    # Log and handle evaluation errors gracefully
                    logger.error(f"Error processing {o_key} with {i_key}: {e}")
                    input_data[i_key] = f"Error: {e}"
            else:
                # Save the original input value or None if O\d_eq or I\d is missing
                input_data[i_key] = kwargs.get(i_key, None)



        # Step 3: Log the collected input data for debugging
        logger.debug(f"Collected input data: {input_data}")
        self.done(x=str(input_data))
        return tuple(input_data.get(f"I{i}", None) for i in range(1, 9))


        #context = {key: value for key, value in kwargs.items() if value is not None}
        results = [None] * 8

        if params == "" and any(value is not None for value in kwargs.values()):
            # Iterate over the expected input keys (`I1`, `I2`, ..., `I8`)
            context = {}
            for i in range(9, 16):
                input_key = f"I{i + 1}"  # I1, I2, ..., I8
                if input_key in kwargs and kwargs[input_key] is not None:
                    # Simply store the object reference in the context directly
                    context[f"result_{input_key}"] = kwargs[input_key]
                    # Add to the appropriate output slot
                    results[i] = context[f"result_{input_key}"]

            # Return the results as a tuple
            return tuple(results)

        # Handle the case where `params` is not empty
        try:
            context = {key: value for key, value in kwargs.items() if value is not None}
            code = f"result = {params}"
            exec(code, globals(), context)
            return self.done(x=str(context["result"]))
        except Exception as e:
            # Handle errors gracefully
            return self.done(x=f"Exception occurred: {e}")



@log_all
class DebugAny2:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                #"presets": (DEBUGANY_OPTS, ),
                "params": ("STRING", {"multiline": False, "default": "", "defaultInput": False}),
            },
            "optional": {
                "a": (anytype, {"forceInput": True}),
                #"b": (anytype, {"forceInput": True}),
                #"script": ("STRING", {"forceInput": True}),
            }
        }
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    CATEGORY = CATEGORY.MAIN.value
    FUNCTION = "display_x"

    def done(self, x):
        if len(str(x)) > 5000:
            x = str(x)[:5000] + "...Too long string"
        return {
            "ui": {
                "string": [x, ]
            },
            "result": (x,)
        }
    def display_x(self, params="", a=None) -> str:
        if params == "" and a is None:
            return self.done(x="")
        elif params == "" and a is not None:
            if isinstance(a, str):
                code = f"result = {str(a)}"
            else:
                code = f"result = {a}"
        else:
            code = f"result = {params}"
        context = {"a": a}
        exec(code, globals(), context)
        return self.done(x=str(context["result"]))

