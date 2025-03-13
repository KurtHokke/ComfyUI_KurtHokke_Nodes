from ..utils import CATEGORY, parse_string_to_list
import comfy.model_management
from nodes import MAX_RESOLUTION
import torch
import comfy.samplers
import comfy.sample
import folder_paths


class EmptyLatentSize:
    def __init__(self):
        self.device = comfy.model_management.intermediate_device()

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "width": ("INT", {"default": 1024, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
            "height": ("INT", {"default": 1024, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
            }}

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value
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

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value
    RETURN_TYPES = ("LATENT","INT","INT",)
    RETURN_NAMES = ("LATENT","width","height",)
    FUNCTION = "execute"

    def execute(self, width=0, height=0):

        latent = torch.zeros([1, 4, height // 8, width // 8], device=self.device)

        return ({"samples":latent}, width, height,)


class SamplerSel:
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value
    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_names"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"sampler_name": (comfy.samplers.KSampler.SAMPLERS,)}}

    def get_names(self, sampler_name):
        return (sampler_name,)


class SchedulerSel:
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value
    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_names"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"scheduler": (comfy.samplers.KSampler.SCHEDULERS,)}}

    def get_names(self, scheduler):
        return (scheduler,)


class LoraFluxParams:
    @classmethod
    def INPUT_TYPES(s):
        optional_loras = ['none'] + folder_paths.get_filename_list("loras")
        return {
            "required": {
                "lora_1": (folder_paths.get_filename_list("loras"), {"tooltip": "The name of the LoRA."}),
                "strength_lora_1": ("STRING", { "multiline": False, "dynamicPrompts": False, "default": "1.0" }),
            },
            "optional": {
                "lora_2": (optional_loras, ),
                "strength_lora_2": ("STRING", { "multiline": False, "dynamicPrompts": False }),
                "lora_3": (optional_loras, ),
                "strength_lora_3": ("STRING", { "multiline": False, "dynamicPrompts": False }),
                "lora_4": (optional_loras, ),
                "strength_lora_4": ("STRING", { "multiline": False, "dynamicPrompts": False }),
                "lora_5": (optional_loras, ),
                "strength_lora_5": ("STRING", { "multiline": False, "dynamicPrompts": False }),
                "lora_6": (optional_loras, ),
                "strength_lora_6": ("STRING", { "multiline": False, "dynamicPrompts": False }),
                "lora_7": (optional_loras, ),
                "strength_lora_7": ("STRING", { "multiline": False, "dynamicPrompts": False }),
            }
        }

    RETURN_TYPES = ("LORA_PARAMS", )
    FUNCTION = "execute"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.ADVANCED.value

    def execute(self, lora_1, strength_lora_1, lora_2="none", strength_lora_2="", lora_3="none", strength_lora_3="", lora_4="none", strength_lora_4="", lora_5="none", strength_lora_5="", lora_6="none", strength_lora_6="", lora_7="none", strength_lora_7=""):
        output = { "loras": [], "strengths": [] }
        output["loras"].append(lora_1)
        output["strengths"].append(parse_string_to_list(strength_lora_1))

        if lora_2 != "none":
            output["loras"].append(lora_2)
            if strength_lora_2 == "":
                strength_lora_2 = "1.0"
            output["strengths"].append(parse_string_to_list(strength_lora_2))
        if lora_3 != "none":
            output["loras"].append(lora_3)
            if strength_lora_3 == "":
                strength_lora_3 = "1.0"
            output["strengths"].append(parse_string_to_list(strength_lora_3))
        if lora_4 != "none":
            output["loras"].append(lora_4)
            if strength_lora_4 == "":
                strength_lora_4 = "1.0"
            output["strengths"].append(parse_string_to_list(strength_lora_4))
        if lora_5 != "none":
            output["loras"].append(lora_5)
            if strength_lora_5 == "":
                strength_lora_5 = "1.0"
            output["strengths"].append(parse_string_to_list(strength_lora_5))
        if lora_6 != "none":
            output["loras"].append(lora_6)
            if strength_lora_6 == "":
                strength_lora_6 = "1.0"
            output["strengths"].append(parse_string_to_list(strength_lora_6))
        if lora_7 != "none":
            output["loras"].append(lora_7)
            if strength_lora_7 == "":
                strength_lora_7 = "1.0"
            output["strengths"].append(parse_string_to_list(strength_lora_7))

        return (output,)