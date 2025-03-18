from ..utils import CATEGORY, any
from ..helpers import DataHandler
from ..helpers import ConfigManager, restricted_import, original_import
from ..loggers import get_logger
import builtins
import black
import json
import re

logger, log_all = get_logger("log_all")


debugany_config = ConfigManager("debugany.config")

DEBUGANY_BASEOPTS = ["None", "Save script", "Call Attributes"]
DEBUGANY_OPTS = debugany_config.generate_list(DEBUGANY_BASEOPTS, "debugany.config")

@log_all
class DebugAny:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "presets": (DEBUGANY_OPTS, ),
                "params": ("STRING", {"multiline": False, "default": "", "defaultInput": False}),
            },
            "optional": {
                "a": (any, {"forceInput": True}),
                "b": (any, {"forceInput": True}),
                "script": ("STRING", {"forceInput": True}),
            }
        }
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    CATEGORY = CATEGORY.MAIN.value
    FUNCTION = "display_x"

    def validate_code(self, params, func_code):
        params = params.strip()
        params = re.sub(r"\)$", "):", params)
        params = re.sub(r"^(\w+\()", r"def \1", params)
        logger.debug(f"params: {params}")
        commas = re.findall(r"(\w|\d),\s", params)
        colons = re.findall(r"(\w|\d):\s", params)
        equals = re.findall(r"(\w|\d)=\w", params)
        if len(commas) != params.count(","):
            params = re.sub(r",(\w)", r", \1", params)
        if len(colons) != params.count(":") - 1:
            params = re.sub(r":(\w)", r": \1", params)
        if len(equals) != params.count("="):
            params = re.sub(r"\s*=\s*", r"=", params)
        func_name = re.sub(r"^def\s(\w+)\(.*", r"\1", params)
        import textwrap
        logger.debug(f"params: {params}\nfunc_code: {func_code}")
        func_code = textwrap.indent(func_code, "    ")
        valid_code = black.format_str(f"{params}\n{func_code}", mode=black.Mode())
        return func_name, valid_code

    def debug_exec(self, func_code: str, parameters: str, context: dict = None, skip_validation: bool = False):
        """Executes arbitrary Python code for debugging purposes only."""
        if not skip_validation:
            func_name, valid_code = self.validate_code(parameters, func_code)
        else:
            func_name = "call_attributes"
            valid_code = func_code

        import inspect
        logger.debug(f"assembled {func_name}():\n{valid_code}")
        if context is None:
            context = {}
        try:
            builtins.__import__ = restricted_import
            exec(valid_code, {}, context)
            function = context[func_name]
            argspec = inspect.getfullargspec(function)
            a = context.get('a', None)
            b = context.get('b', None)

            if argspec.args:
                arguments = {arg: context.get(arg) for arg in argspec.args}
                result = function(**arguments)
            else:
                result = function()

            return str(result)
        except Exception as e:
            logger.error(f"Error executing code: {e}", exc_info=True)
            return {"error": str(e)}
        finally:
            builtins.__import__ = original_import
    def done(self, x):
        return {
            "ui": {
                "string": [x, ]
            },
            "result": (x,)
        }
    def display_x(self, presets, params="", script=None, a=None, b=None):
        if script == "":
            script = None

        if "None" in presets:
            if script is None:
                return self.done(x=f"{str(a)}")
            elif params != "":
                try:
                    return self.done(x=str(self.debug_exec(script, parameters=params, context={"a": a, "b": b})))
                except Exception as e:
                    return self.done(x=f"Error: {e}",)

        if presets == "Call Attributes":
            if params != "":
                try:
                    script = params
                    return self.done(x=str(self.debug_exec(script, parameters=params, context={"a": a, "b": b}, skip_validation=True)))
                except Exception as e:
                    return self.done(x=f"Error: {e}",)

        if presets == "Save script" and script is not None:
            try:
                script = black.format_str(script, mode=black.Mode())
                script_saved = debugany_config.append_to_config(script, "debugany.config")
                DEBUGANY_OPTS = debugany_config.generate_list(DEBUGANY_BASEOPTS, "debugany.config")
                return self.done(x=str(script_saved))
            except Exception as e:
                return self.done(x=f"Error: {e}",)
