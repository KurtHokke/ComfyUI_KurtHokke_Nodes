from custom_nodes.ComfyUI_KurtHokke_Nodes.utils import CATEGORY, prefix
import folder_paths
import os
from io import BytesIO
import tempfile
from PIL import Image


class CreateMask:
    @classmethod
    def INPUT_TYPES(s):
        nodesdir = os.path.dirname(os.path.abspath(__file__))
        node_input_dir = os.path.normpath(os.path.join(nodesdir, "../img"))
        input_dir = os.path.join(node_input_dir, folder_paths.get_input_directory())
        input_dir = os.path.normpath(input_dir)
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {"required":
                    {"image": (sorted(files), {"image_upload": True})},
                }
    RETURN_TYPES = ("MASK", "IMAGE")
    FUNCTION = "create_mask"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.TOOLS.value

    def create_mask(self, image):
        from nodes import LoadImage
        get_loadimage = LoadImage()
        if not image:
            return (None, None)
        width, height = 1024, 1024
        white_color = (255, 255, 255)
        generated_image = Image.new("RGB", (width, height), white_color)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            generated_image.save(temp_file.name)
            temp_file_path = temp_file.name

        # Pass the temp file path to load_image
        new_image, new_mask = get_loadimage.load_image(temp_file_path)


        return (new_mask, new_image)