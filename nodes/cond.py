from ..utils import CATEGORY
from comfy.comfy_types import IO, ComfyNodeABC, InputTypeDict, FileLocator
from nodes import CLIPTextEncode


class CLIPTextEncode_Pipe(ComfyNodeABC):
    @classmethod
    def INPUT_TYPES(s) -> InputTypeDict:
        return {
            "required": {
                "text": (IO.STRING, {"multiline": True, "dynamicPrompts": True, "tooltip": "The text to be encoded."}),
                "UnetClipPipe": ("UnetClipPipe",)
            }
        }
    RETURN_TYPES = (IO.CONDITIONING,)
    OUTPUT_TOOLTIPS = ("A conditioning containing the embedded text used to guide the diffusion model.",)
    FUNCTION = "encode"

    CATEGORY = CATEGORY.MAIN.value + "/Conditioning"
    DESCRIPTION = "Encodes a text prompt using a CLIP model into an embedding that can be used to guide the diffusion model towards generating specific images."

    def encode(self, UnetClipPipe, text):
        model, clip = UnetClipPipe
        
        get_CLIPTextEncode = CLIPTextEncode()
        conditioning = get_CLIPTextEncode.encode(clip, text)[0]

        return (conditioning, )