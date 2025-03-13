from ..utils import CATEGORY, any
import json

class ExecutePythonNode:
    @classmethod
    def INPUT_TYPES(cls):
        # Define the input sliders, text fields, values, etc.
        return {
            "required": {
                "python_code": ("STRING", {"multiline": True})  # Input: Python code to execute
            },
            "optional": {
                "a": (any, )
            }
        }

    RETURN_TYPES = (any, )  # Define output types: here, just a string for results or errors
    FUNCTION = "execute_python_code"  # The function to be called to process inputs

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.TOOLS.value

    @staticmethod
    def execute_python_code(python_code, a=None):
        try:
            # Create a local execution scope
            exec_scope = {"a": a}

            # Execute the code in the local scope
            exec(python_code, {}, exec_scope)

            # Attempt to retrieve the result from the scope
            if "result" in exec_scope:
                output = exec_scope["result"]  # 'result' is the expected output variable.
            else:
                return (None,)  # If no 'result' is defined in code, return None.

            # Try returning the result directly if it's a basic Python object
            if isinstance(output, (str, int, float, list, dict, tuple, bool)):
                return (output,)
            else:
                # Convert to a universal format (JSON) if it can't be directly returned
                try:
                    return (json.dumps(output),)  # Serialize to a JSON string
                except TypeError:
                    return (str(output),)  # Fallback to string conversion in case of issues
        except Exception as e:
            # Return the error message as a string if code execution fails
            return (f"Error: {e}",)

