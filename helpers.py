from typing import List, Union, Optional
from pathlib import Path
import folder_paths
from .loggers import get_logger
import os
import re

log_function = get_logger("log_function")
log_return = get_logger("log_return")
logger, log_all = get_logger("log_all")
#
class ConfigManager:
    @log_function
    def __init__(self, config_name: str) -> None:
        self.config_dir = Path(os.path.join(folder_paths.get_user_directory(), "default", "kurthokke_nodes"))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_name = config_name
        self.config_path = self.config_dir / config_name
    @log_return
    def append_to_config(self, string: str, config_name: str) -> None:
        if config_name == self.config_name:
            with open(self.config_path, "a") as f:
                f.write(f"{string}\n")
            return f"\nsaved:\n{string} >> {self.config_path}"

    def generate_list(self, base_list: list, config_name: str, prepend: bool = False) -> list:
        logger.info(f"config_name: {config_name}")
        logger.info(f"base_list: {base_list}")
        logger.info(f"config_path: {self.config_path}")
        if config_name == self.config_name and self.config_path.exists():
            with open(self.config_path, "r") as f:
                lines = f.read().splitlines()
            custom_list = []
            for line in lines:
                if re.match(r'^def \w+\(.*\):$', line):
                    custom_list.append(line)
            if prepend:
                logger.info(f"custom_list: {custom_list} + base_list: {base_list}")
                return custom_list + base_list
            else:
                logger.info(f"base_list: {base_list} + custom_list: {custom_list}")
                return base_list + custom_list
        else:
            logger.info(f"No config file found at {self.config_path}")
            return base_list


import builtins
DISALLOWED_IMPORTS = {"os", "subprocess"}
original_import = builtins.__import__
def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    """A restricted version of __import__ that only allows modules not in a blacklist."""
    if name in DISALLOWED_IMPORTS:
        raise ImportError(f"Import of '{name}' is not allowed.")
    return original_import(name, globals, locals, fromlist, level)


