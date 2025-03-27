from custom_nodes.ComfyUI_KurtHokke_Nodes.utils import CATEGORY, any, prefix
import subprocess

class BashScriptNode:
    """
    A custom ComfyUI node that allows users to input a bash script and executes it.
    """

    @classmethod
    def INPUT_TYPES(cls):
        # Define inputs for the node
        return {
            "required": {
                "bash_script": ("STRING", {"multiline": True, "default": "echo 'Hello from Bash!'"}),
            },
            "optional": {
                "a": (any, ),
                "b": (any, ),
            }
        }

    RETURN_TYPES = ("STRING",)  # Output type of the node
    FUNCTION = "execute_bash"  # Function to run when the node is executed
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.TOOLS.value

    def execute_bash(self, bash_script, a=None, b=None):
        """
        Executes the bash script provided by the user.

        Args:
            bash_script (str): The bash script to execute.

        Returns:
            tuple: Output of the bash script or error messages.
        """
        variable_declarations = []
        if a is not None:
            variable_declarations.append(f"a='{a}'")
        if b is not None:
            variable_declarations.append(f"b='{b}'")

        # Create the final script
        complete_script = "\n".join(variable_declarations) + "\n" + bash_script

        try:
            # Use subprocess to execute the complete Bash script
            result = subprocess.run(
                ["bash", "-c", complete_script],  # Execute the bash script with variables prepended
                text=True,  # Capture output as text
                capture_output=True,  # Capture stdout and stderr separately
                check=True  # Raise an exception for non-zero exit codes
            )
            return (result.stdout.strip(),)  # Return stdout
        except subprocess.CalledProcessError as e:
            # Return detailed error messages from stderr
            return (f"Bash Error: {e.stderr.strip()}",)
        except Exception as e:
            # Catch-all for unexpected Python-level errors
            return (f"Error: {str(e)}",)

