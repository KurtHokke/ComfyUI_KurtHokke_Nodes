
from .utils import get_node_dir
import importlib.util
import glob
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

def init():
    nodes = get_node_dir("nodes")
    files = glob.glob(os.path.join(nodes, "*.py"), recursive=False)
    for file in files:
        module_name = os.path.splitext(os.path.basename(file))[0]
        package_name = f"ComfyUI_KurtHokke_Nodes.nodes.{module_name}"  # Full package path here

        # Create a module specification with the package name
        spec = importlib.util.spec_from_file_location(package_name, file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[package_name] = module
        spec.loader.exec_module(module)

        if hasattr(module, "NODE_CLASS_MAPPINGS") and getattr(module, "NODE_CLASS_MAPPINGS") is not None:
            NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
            if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS") and getattr(module, "NODE_DISPLAY_NAME_MAPPINGS") is not None:
                NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)

init()
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
WEB_DIRECTORY = "./web"

