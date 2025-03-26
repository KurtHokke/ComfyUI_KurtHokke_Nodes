from khn.utils import CATEGORY, prefix
import json
import folder_paths
import re


class get_lora_metadata:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "lora_name": (folder_paths.get_filename_list("loras"),),
            },
            "optional": {
                "filter": ("STRING", {"defaultInput": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("tags", "tag_per_line")
    FUNCTION = "get_metadata"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.TOOLS.value

    def get_metadata(self, lora_name, filter=None):
        try:
            lora_path = folder_paths.get_full_path("loras", lora_name)
            with open(lora_path, "rb") as file:
                header_size = int.from_bytes(file.read(8), "little", signed=False)

                if header_size <= 0:
                    raise BufferError("Invalid header size")

                header = file.read(header_size)
                header_json = json.loads(header)

                metadata = header_json.get("__metadata__", {})
                tags = metadata.get("ss_tag_frequency", None)

                if tags:
                    tags_dict = json.loads(tags)
                    first_key = next(iter(tags_dict))
                    before_tags = tags_dict[first_key]

                    # Retain spaces in cleaning logic
                    cleaned_tags = re.sub(r"[^\w, ]", "", str(before_tags))
                    all_tags = re.sub(r",\s*", ", ", cleaned_tags)  # Ensure single space after commas
                    tag_per_line = all_tags.replace(", ", ",\n")  # Newline-separated tags

                    if filter:
                        filter_tags = set(filter.split(','))  # Avoid stripping spaces
                        all_tags = ', '.join([tag for tag in all_tags.split(', ') if tag in filter_tags])

                    return all_tags, tag_per_line
                else:
                    raise ValueError("No tags found in the metadata.")
        except Exception as e:
            print(f"Error processing {lora_name}: {e}")
            return None, None


NODE_CLASS_MAPPINGS = {
    "get_lora_metadata": get_lora_metadata,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "get_lora_metadata": prefix + "get_lora_metadata",
}