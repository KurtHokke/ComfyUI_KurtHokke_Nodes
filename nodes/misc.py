from ..names import CATEGORY
import comfy.model_management
from nodes import MAX_RESOLUTION
import torch

class EmptyLatentSize:
    def __init__(self):
        self.device = comfy.model_management.intermediate_device()

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "width": ("INT", {"default": 1024, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
            "height": ("INT", {"default": 1024, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
            }}

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.MISC.value
    RETURN_TYPES = ("LATENT","INT","INT",)
    RETURN_NAMES = ("LATENT","width","height",)
    FUNCTION = "execute"

    def execute(self, width=0, height=0):

        latent = torch.zeros([1, 4, height // 8, width // 8], device=self.device)

        return ({"samples":latent}, width, height,)


class EmptyLatentSize64:
    def __init__(self):
        self.device = comfy.model_management.intermediate_device()

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "width": ("INT", {"default": 1024, "min": 0, "max": MAX_RESOLUTION, "step": 64}),
            "height": ("INT", {"default": 1024, "min": 0, "max": MAX_RESOLUTION, "step": 64}),
            }}

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.MISC.value
    RETURN_TYPES = ("LATENT","INT","INT",)
    RETURN_NAMES = ("LATENT","width","height",)
    FUNCTION = "execute"

    def execute(self, width=0, height=0):

        latent = torch.zeros([1, 4, height // 8, width // 8], device=self.device)

        return ({"samples":latent}, width, height,)