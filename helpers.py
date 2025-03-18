from typing import List, Union, Optional
from pathlib import Path
import folder_paths
from .loggers import get_logger
import os
import re
import importlib.util
import sys

logger, decoDebug = get_logger("all")
log_function = get_logger("function")
#
class ConfigManager:
    def __init__(self, config_name: str) -> None:
        self.config_dir = Path(os.path.join(folder_paths.get_user_directory(), "default", "kurthokke_nodes"))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_name = config_name
        self.config_path = self.config_dir / config_name
    def append_to_config(self, string: str, config_name: str) -> None:
        if config_name == self.config_name:
            with open(self.config_path, "a") as f:
                f.write(f"{string}\n")
            return f"\nsaved:\n{string} >> {self.config_path}"

    def generate_list(self, base_list: list, config_name: str, prepend: bool = False) -> list:
        logger.debug(f"config_name: {config_name}")
        logger.debug(f"base_list: {base_list}")
        logger.debug(f"config_path: {self.config_path}")
        if config_name == self.config_name and self.config_path.exists():
            with open(self.config_path, "r") as f:
                lines = f.read().splitlines()
            custom_list = []
            for line in lines:
                if re.match(r'^def \w+\(.*\):$', line):
                    custom_list.append(line)
            if prepend:
                logger.debug(f"custom_list: {custom_list} + base_list: {base_list}")
                return custom_list + base_list
            else:
                logger.debug(f"base_list: {base_list} + custom_list: {custom_list}")
                return base_list + custom_list
        else:
            logger.debug(f"No config file found at {self.config_path}")
            return base_list
@log_function
def import_class_from_file(class_name, file_path):
    """
    Import a specific class from a Python file dynamically.
    Args:
        class_name (str): The name of the class to import.
        file_path (str): The path to the Python file containing the class.
    Returns:
        type: The imported class, or None if the class was not found.
    """
    module_name = os.path.splitext(os.path.basename(file_path))[0]  # Get module name from the file name
    project_root = sys.path  # Adjust this to your project root

    # Add project root to sys.path if it's not already included
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Import the module dynamically
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # Load the module
        cls = getattr(module, class_name, None)  # Retrieve the class from the module
        if cls is None:
            print(f"Class '{class_name}' not found in the specified file.")
        return cls
    except Exception as e:
        print(f"Failed to import module from {file_path}: {e}")
        return None
    finally:
        # Remove the project root afterward if you want clean imports (not always necessary)
        if project_root in sys.path:
            sys.path.remove(project_root)

@log_function
def find_class_in_files(directory, class_name):
    """
    Search for a class definition in all .py files in the given directory (recursively).

    Args:
        directory (str): The root directory to search in.
        class_name (str): The name of the class to search for.

    Returns:
        list: A list of file paths and line numbers where the class is defined.
    """
    results = []
    class_pattern = re.compile(rf"class\s+{class_name}\b")  # Regex: matches "class <class_name>"

    # Walk through all files in the directory and subdirectories
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):  # Only look at Python files
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line_number, line in enumerate(f, start=1):
                            if class_pattern.search(line):  # Match the class pattern
                                results.append((file_path, line_number, line.strip()))
                except Exception as e:
                    print(f"Could not open {file_path}: {e}")

    return results
@log_function
def find_and_import_class(class_name, directory=None, *args, **kwargs):
    """
    Search for a class in all Python files within a directory and dynamically import it.
    Args:
        directory (str): The directory to search in.
        class_name (str): The name of the class to search for.
        *args: Positional arguments for the class constructor.
        **kwargs: Keyword arguments for the class constructor.
    Returns:
        object: An instance of the imported class, or None if not found.
    """
    if directory is None:
        directory = os.path.dirname(os.path.abspath(__file__))

    # Step 1: Find the class in the files
    matches = find_class_in_files(directory, class_name)
    if not matches:
        print(f"Class '{class_name}' not found in any .py file under {directory}.")
        return None

    # Step 2: Import the class from the first matching file
    for file_path, _, _ in matches:
        cls = import_class_from_file(class_name, file_path)
        if cls:
            try:
                # Step 3: Instantiate the class with provided arguments
                instance = cls(*args, **kwargs)
                print(f"Successfully created an instance of '{class_name}' from '{file_path}'.")
                return instance
            except TypeError as e:
                print(f"Failed to create an instance of '{class_name}': {e}")
                return None

    print(f"Class '{class_name}' found but could not be instantiated.")
    return None



class DataHandler:
    def is_instance_recursive(self, flattened_obj, obj_is=None):
        if obj_is is None:
            obj_is = {}
        for item in flattened_obj:
            recursive_obj_is = self.is_instance(item, obj_is=obj_is, start=False)
            obj_is = {**obj_is, **recursive_obj_is}
        return obj_is

    def is_instance(self, obj, obj_is=None, start=True):
        from torch import Tensor
        if obj_is is None and start is True:
            obj_is = {}
        if isinstance(obj, dict):
            obj_is = {**obj_is, "dict": True}
        if isinstance(obj, list):
            obj_is = {**obj_is, "list": True}
            flattened_obj = self.flatten(obj)
            item_types = self.is_instance_recursive(flattened_obj, obj_is)
            obj_is = {**obj_is, **item_types}

        if isinstance(obj, tuple):
            obj_is = {**obj_is, "tuple": True}
            obj_len = len(obj)
            for i in range(obj_len):
                if isinstance(obj[i], list):
                    flattened_obj = self.flatten(obj[i])
                    item_types = self.is_instance_recursive(flattened_obj, obj_is)
                    obj_is = {**obj_is, **item_types}
                else:
                    item_types = self.is_instance(obj[i], obj_is=obj_is, start=False)
                    obj_is = {**obj_is, **item_types}
        if isinstance(obj, str):
            obj_is = {**obj_is, "str": True}
        if isinstance(obj, int):
            obj_is = {**obj_is, "int": True}
        if isinstance(obj, float):
            obj_is = {**obj_is, "float": True}
        if isinstance(obj, bool):
            obj_is = {**obj_is, "bool": True}
        if isinstance(obj, bytes):
            obj_is = {**obj_is, "bytes": True}
        if isinstance(obj, Tensor):
            obj_is = {**obj_is, "tensor": True}
        if obj_is == {}:
            obj_is = {**obj_is, "UNSOLVED_TYPE": True}
        return obj_is

    def flatten(self, nested):
        if not isinstance(nested, (list, tuple)):
            return [nested]
        flattened = []
        for item in nested:
            flattened.extend(self.flatten(item))
        return flattened

    def mod_tensors(self, tensors, operation):
        if isinstance(tensors, list):
            pooled_output = tensors[0][1]['pooled_output']
            tensor = self.flatten(tensors)[0]

            if operation == "norm_tensor":
                tensor = (tensor - tensor.min()) / (tensor.max() - tensor.min())
            elif operation == "standardize_tensor":
                tensor = (tensor - tensor.mean()) / tensor.std()
            elif operation == "pool_mean":
                tensor = tensor.mean(dim=2)
            elif operation == "pool_max":
                tensor = tensor.max(dim=2).values
            elif operation == "pool_sequence":
                tensor = tensor.mean(dim=1)
            elif operation == "clamp_tensor":
                tensor = tensor.clamp(min=-10, max=10)
            elif operation == "squeeze_tensor":
                tensor = tensor.squeeze(0)

            pooled_output = {'pooled_output': pooled_output}
            tensors = [[tensor] + [pooled_output]]
            return tensors



def nesting_depth(seq):
    from collections.abc import Sequence
    from itertools import chain, count
    if isinstance(seq, tuple):
        logger.debug(f"tuple detected: {type(seq)}")
        seq = seq[0]
        logger.debug(f"Should now be list: {type(seq)}")
    if isinstance(seq, list):
        for level in count():
            if not seq:
                return level
            seq = list(chain.from_iterable(s for s in seq if isinstance(s, Sequence)))
            logger.debug(f"LOOP")
    else:
        level = 0
        return level

def multiply_tensors(tensors, factor=1.0, left_f=None, right_f=None):
    if isinstance(tensors, list):
        get_datahandler = DataHandler()
        pooled_output = tensors[0][1]['pooled_output']
        tensors = get_datahandler.flatten(tensors)[0]
        if left_f is None and right_f is None:
            left_f = factor
            right_f = factor
        tensors = tensors * left_f
        pooled_output = pooled_output * right_f
        pooled_output = {'pooled_output': pooled_output}
        tensors = [[tensors] + [pooled_output]]
        return tensors

def check_string(string: (str, list[str])) -> (str, list[str]):
    if isinstance(string, str):
        if len(str(string)) > 5000:
            string = str(string)[:5000] + "...Too long string"
        return string
    else:
        return f"!!!\n{string} IS NOT A STRING\n!!!"


import builtins
DISALLOWED_IMPORTS = {"os", "subprocess"}
original_import = builtins.__import__
def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    """A restricted version of __import__ that only allows modules not in a blacklist."""
    if name in DISALLOWED_IMPORTS:
        raise ImportError(f"Import of '{name}' is not allowed.")
    return original_import(name, globals, locals, fromlist, level)


