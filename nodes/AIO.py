from khn.utils import CATEGORY, MODEL_TYPES, any, prefix
from khn.loggers import get_logger
from khn.core import SampleAssembler
from sympy.strategies.branch import debug

from comfy.comfy_types import *
import comfy.samplers
from comfy_extras.nodes_custom_sampler import SamplerCustomAdvanced, BasicScheduler, BetaSamplingScheduler
from nodes import MAX_RESOLUTION
import torch

logger, log_all = get_logger("log_all")

class AIO:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processAIO = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                #"model_type": (MODEL_TYPES, ),
                "cfg_guidance": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.01}),
                "sampler_name": (comfy.samplers.SAMPLER_NAMES, ),
                "scheduler": (comfy.samplers.SCHEDULER_NAMES, ),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "denoise": ("FLOAT", {"default": 1.00, "min": 0.00, "max": 1.00, "step": 0.01}),
                "width": ("INT", {"default": 1024, "min": 16, "max": MAX_RESOLUTION, "step": 16}),
                "height": ("INT", {"default": 1024, "min": 16, "max": MAX_RESOLUTION, "step": 16}),
                "noise_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "debug_output": ("BOOLEAN", {"default": False, "defaultInput": False}),
            },
            "optional": {
                "model": ("MODEL", ),
                "vae": ("VAE", ),
                "pos": ("CLIPTEXT_PIPE", ),
                "neg": ("CLIPTEXT_PIPE", ),
                "g_s_s_s": ("GSSS", ),
                "extra_opts": ("EXTRA_OPTS", ),
            }
        }
    RETURN_TYPES = ("SCA_PIPE", )
    RETURN_NAMES = ("SCA_PIPE", )
    FUNCTION = "determine_sample_settings"
    CATEGORY = CATEGORY.MAIN.value

    def determine_sample_settings(self, cfg_guidance: float, sampler_name: list[str], scheduler: list[str],
                                  steps: int, denoise: float, width: int, height: int, noise_seed: int,
                                  debug_output: bool, model=None, vae=None, pos=None, neg=None, g_s_s_s=None, extra_opts=None) -> tuple[list[any]]:
        if extra_opts is None:
            extra_opts = {}
        if pos is not None:
            clip = pos[0]
            pos = pos[1]
            if neg is not None:
                neg = neg[1]
            sca_dict = {
                "model": model,
                "clip": clip,
                "vae": vae,
                "pos": pos,
                "neg": neg,
                "cfg_guid": cfg_guidance,
                "sampler_name": sampler_name,
                "scheduler": scheduler,
                "steps": steps,
                "denoise": denoise,
                "width": width,
                "height": height,
                "g_s_s_s": g_s_s_s,
                "extra_opts": extra_opts,
            }
        else:
            return logger.info("No positive prompts provided")
        if self.processAIO is None:
            self.processAIO = SampleAssembler(sca_dict, debug_output)

        sca_pipe = self.processAIO.update(sca_dict, noise_seed, debug_output)

        return (sca_pipe, )

class SCA_Pipe:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "SCA_PIPE": ("SCA_PIPE", ),
            }
        }

    RETURN_TYPES = ("IMAGE", "LATENT", )
    RETURN_NAMES = ("decoded_image", "output_samples", )

    FUNCTION = "get_sample"

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.ADVANCED.value

    def decode(self, vae, samples):
        images = vae.decode(samples["samples"])[0]

        if len(images.shape) == 5:
            images = images.reshape(-1, images.shape[-3], images.shape[-2], images.shape[-1])
        return (images, )

    def decode_tiled(self, vae, samples, tile_size, overlap=64, temporal_size=64, temporal_overlap=8):
        if tile_size < overlap * 4:
            overlap = tile_size // 4
        if temporal_size < temporal_overlap * 2:
            temporal_overlap = temporal_overlap // 2
        temporal_compression = vae.temporal_compression_decode()
        if temporal_compression is not None:
            temporal_size = max(2, temporal_size // temporal_compression)
            temporal_overlap = max(1, min(temporal_size // 2, temporal_overlap // temporal_compression))
        else:
            temporal_size = None
            temporal_overlap = None

        compression = vae.spacial_compression_decode()
        images = vae.decode_tiled(samples["samples"], tile_x=tile_size // compression, tile_y=tile_size // compression, overlap=overlap // compression, tile_t=temporal_size, overlap_t=temporal_overlap)[0]
        if len(images.shape) == 5:
            images = images.reshape(-1, images.shape[-3], images.shape[-2], images.shape[-1])
        return (images, )

    def get_sample(self, SCA_PIPE):

        get_samplercustomadvanced = SamplerCustomAdvanced()

        noise = SCA_PIPE["noise"]
        guider = SCA_PIPE["guider"]
        sampler = SCA_PIPE["sampler"]
        sigmas = SCA_PIPE["sigmas"]
        latent = SCA_PIPE["samples"]
        vae = SCA_PIPE["vae"]

        out = get_samplercustomadvanced.sample(noise, guider, sampler, sigmas, latent)[0]
        images = self.decode(vae, out)

        return (images, out, )

class extGSSS:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "guider": ("GUIDER", ),
                "sampler": ("SAMPLER", ),
                "sigmas": ("SIGMAS", ),
                "samples": ("LATENT", ),
            }
        }
    RETURN_TYPES = ("GSSS", )
    RETURN_NAMES = ("g_s_s_s", )
    FUNCTION = "pack_gsss"
    CATEGORY = CATEGORY.MAIN.value
    def pack_gsss(self, guider=None, sampler=None, sigmas=None, samples=None):
        gsss = {}
        if guider is not None:
            gsss = {**gsss, "guider": guider}
        if sampler is not None:
            gsss = {**gsss, "sampler": sampler}
        if sigmas is not None:
            gsss = {**gsss, "sigmas": sigmas}
        if samples is not None:
            gsss = {**gsss, "samples": samples}
        g_s_s_s = gsss
        return (g_s_s_s, )


NODE_CLASS_MAPPINGS = {
    "AIO": AIO,
    "SCA_Pipe": SCA_Pipe,
    "extGSSS": extGSSS,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "AIO": prefix + "AIO",
    "SCA_Pipe": prefix + "SCA_Pipe",
    "extGSSS": prefix + "extGSSS",
}