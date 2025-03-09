'''
    !DISCLAIMER! I'm very new to programming and I've been heavily inspired by following.
https://github.com/crystian/ComfyUI-Crystools
https://github.com/cubiq/ComfyUI_essentials
  Many thanks goes to these awesome developers!
'''
from ..utils import any, BOOLEAN, INT, FLOAT, STRING
from ..names import CATEGORY
from comfy_extras.nodes_custom_sampler import SamplerCustomAdvanced
import math
import torch
import time


class SamplerCustomAdvanced_Pipe:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "SCA_PIPE": (any, ),
            }
        }

    RETURN_TYPES = ("LATENT")
    RETURN_NAMES = ("denoised_output")

    FUNCTION = "get_sample"

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

    def get_sample(self, SCA_PIPE=None):
        get_SamplerCustomAdvanced = SamplerCustomAdvanced()

        noise, guider, sampler, sigmas, latent = SCA_PIPE
        out_denoised = get_SamplerCustomAdvanced.sample(noise, guider, sampler, sigmas, latent_image=latent)

        return (out_denoised,)


class BooleanToPipe:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_1": BOOLEAN,
                "boolean_2": BOOLEAN,
                "boolean_3": BOOLEAN,
                "boolean_4": BOOLEAN,
            }
        }

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value
    RETURN_TYPES = ("BoolPipe",)

    FUNCTION = "execute"

    def execute(self, boolean_1=True, boolean_2=True, boolean_3=True, boolean_4=True):

        BoolPipeMod = []

        BoolPipeMod.append(boolean_1)
        BoolPipeMod.append(boolean_2)
        BoolPipeMod.append(boolean_3)
        BoolPipeMod.append(boolean_4)

        return (BoolPipeMod,)

class BooleanFromPipe:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "BoolPipe": (any,),
            },
            "optional": {
            }
        }

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value
    RETURN_TYPES = ("BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN",)
    RETURN_NAMES = ("boolean_1", "boolean_2", "boolean_3", "boolean_4",)

    FUNCTION = "execute"

    def execute(self, BoolPipe=None, ):
        boolean_1, boolean_2, boolean_3, boolean_4, = BoolPipe
        return boolean_1, boolean_2, boolean_3, boolean_4


