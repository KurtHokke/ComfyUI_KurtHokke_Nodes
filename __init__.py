import os
import sys
import importlib

# Define the target path and alias
CUSTOM_NODES_PATH = os.path.join(os.getcwd(), "custom_nodes/ComfyUI_KurtHokke_Nodes")
ALIAS = "khn"

# Add the path to sys.path if it's not already there
if CUSTOM_NODES_PATH not in sys.path:
    sys.path.insert(0, CUSTOM_NODES_PATH)

# Import the package using its actual name
package_name = os.path.basename(CUSTOM_NODES_PATH)  # This gives "ComfyUI_KurtHokke_Nodes"
package = importlib.import_module(package_name)  # Import the package

# Set an alias in sys.modules
sys.modules[ALIAS] = package
sys.modules["khn"] = sys.modules[__name__]


from khn.utils import get_node_dir
import importlib.util
import glob

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

def init():
    nodes = get_node_dir("nodes")
    files = glob.glob(os.path.join(nodes, "*.py"), recursive=False)
    for file in files:
        name = os.path.splitext(file)[0]
        spec = importlib.util.spec_from_file_location(name, file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        if hasattr(module, "NODE_CLASS_MAPPINGS") and getattr(module, "NODE_CLASS_MAPPINGS") is not None:
            NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
            if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS") and getattr(module, "NODE_DISPLAY_NAME_MAPPINGS") is not None:
                NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)

init()
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
WEB_DIRECTORY = "./web"

