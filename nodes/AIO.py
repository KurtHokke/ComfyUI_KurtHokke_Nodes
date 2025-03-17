from ..utils import CATEGORY, MODEL_TYPES, any
from ..loggers import get_logger
import comfy.samplers
from nodes import MAX_RESOLUTION
import torch

logger, log_all = get_logger("log_all")

class AIO_Tuner_Pipe:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                #"model_type": (MODEL_TYPES, ),
                "guidance": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.01}),
                "sampler_name": (comfy.samplers.SAMPLER_NAMES, ),
                "scheduler": (comfy.samplers.SCHEDULER_NAMES, ),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "denoise": ("FLOAT", {"default": "1"}),
                "width": ("INT", {"default": 1024, "min": 16, "max": MAX_RESOLUTION, "step": 16}),
                "height": ("INT", {"default": 1024, "min": 16, "max": MAX_RESOLUTION, "step": 16}),
                "noise_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "model": ("MODEL", ),
                "positive": ("CONDITIONING", ),
                "negative": ("CONDITIONING", ),
                "vae": ("VAE", ),
                "guider": ("GUIDER", ),
                "sampler": ("SAMPLER", ),
                "sigmas": ("SIGMAS", ),
                "samples": ("LATENT", ),
                "extra_opts": ("EXTRA_OPTS", ),
            }
        }
    RETURN_TYPES = ("SCA_PIPE", )
    RETURN_NAMES = ("SCA_PIPE", )
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.ADVANCED.value

    FUNCTION = "determine_pipe_settings"