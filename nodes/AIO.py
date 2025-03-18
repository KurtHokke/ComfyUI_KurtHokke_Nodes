from ..utils import CATEGORY, MODEL_TYPES, any
from ..loggers import get_logger
from ..core import SampleAssembler
from comfy.comfy_types import *
import comfy.samplers
from nodes import MAX_RESOLUTION
import torch

logger, log_all = get_logger("log_all")

class AIO:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                #"model_type": (MODEL_TYPES, ),
                "cfg_guidance": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.01}),
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
                "pos": ("CLIPTEXT_PIPE", ),
                "neg": ("CLIPTEXT_PIPE", ),
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
    FUNCTION = "determine_sample_settings"
    CATEGORY = CATEGORY.MAIN.value

    def determine_sample_settings(self, cfg_guidance: float, sampler_name: list[str], scheduler: list[str],
                                  steps: int, denoise: float, width: int, height: int, noise_seed: int,
                                  model=None, pos=None, neg=None, vae=None, guider=None, sampler=None,
                                  sigmas=None, samples=None, extra_opts=None) -> tuple[list[any]]:

        sca_pipe = [cfg_guidance, sampler_name, scheduler, steps, denoise, width, height, noise_seed, model, vae, guider, sampler, sigmas, samples, extra_opts]
        if guider is not None:
            return (sca_pipe, )
        clip = pos[0]
        models = [model, clip, vae]
        processAIO = SampleAssembler(models)
        pos_prompt = []
        neg_prompt = []
        for i in range(1, len(pos)):
            pos_prompt.append(pos[i])
        if neg is not None:
            for i in range(1, len(neg)):
                neg_prompt.append(neg[i])
        processAIO.update_prompts(pos_prompt, neg_prompt)


        return (sca_pipe, )











