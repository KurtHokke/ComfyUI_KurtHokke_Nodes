from ..utils import CATEGORY
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
    CATEGORY = CATEGORY.MAIN.value + ""

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

                    # Simplified regex processing
                    cleaned_tags = re.sub(r"[^\w,]", "", str(before_tags))  # Only keep alphanumeric and commas
                    all_tags = re.sub(r",\s*", ",\n", cleaned_tags)
                    tag_per_line = all_tags.replace(", ", ",\n")  # Tag per line format

                    if filter:
                        filter_tags = set(map(str.strip, filter.split(',')))
                        all_tags = ', '.join([tag for tag in all_tags.split(', ') if tag in filter_tags])

                    return all_tags, tag_per_line
                else:
                    raise ValueError("No tags found in the metadata.")
        except Exception as e:
            print(f"Error processing {lora_name}: {e}")
            return None, None

'''
class get_lora_metadata:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "lora_name": (folder_paths.get_filename_list("loras"), ),
            },
            "optional": {
                "filter": ("STRING", {"defaultInput": True}),
            }
        }
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("tags", "tag_per_line")
    FUNCTION = "get_metadata"
    CATEGORY = CATEGORY.MAIN.value + ""

    def get_metadata(self, lora_name, filter=None):
        lora_path = folder_paths.get_full_path("loras", lora_name)
        with open(lora_path, "rb") as file:
            # https://github.com/huggingface/safetensor#format
            # 8 bytes: N, an unsigned little-endian 64-bit integer, containing the size of the header
            header_size = int.from_bytes(file.read(8), "little", signed=False)

            if header_size <= 0:
                raise BufferError("Invalid header size")

            header = file.read(header_size)
            if header_size <= 0:
                raise BufferError("Invalid header")

            header_json = json.loads(header)
            tags = header_json["__metadata__"]["ss_tag_frequency"] if "__metadata__" in header_json else None
            tags_dict = json.loads(tags)
            first_key = next(iter(tags_dict))
            before_tags = tags_dict[first_key]
            strip1 = re.sub(r'^{', '', str(before_tags))
            strip2 = re.sub(r': \d+}$', ', ', strip1)
            strip3 = re.sub(r"'", '', strip2)
            all_tags = re.sub(r': \d+,', ',', strip3)
            tag_per_line = re.sub(r', ', ', \n', all_tags)
            if filter is not None:
                filter_tags = filter.split(',')
                for filter_tag in enumerate(filter_tags):
                    filter_tag1 = re.sub(r"^\(\d,'", '', str(filter_tag))
                    filter_tag2 = re.sub(r"'\)$", '', filter_tag1)
                    stripws = re.sub(r' ', '', filter_tag2)
                    addtrailing = re.sub(r'$', ', ', stripws)
                    #filter_pattern = re.escape(addtrailing)
                    all_tags = re.sub(addtrailing, '', all_tags)
                    print(addtrailing)
                #all_tags = filter_tags
        return (all_tags, tag_per_line)
'''