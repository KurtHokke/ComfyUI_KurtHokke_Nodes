from ..utils import CATEGORY, MODEL_TYPES, any, log_function_call, logger
from comfy.comfy_types import *
import node_helpers
import comfy.samplers
from nodes import EmptyLatentImage, MAX_RESOLUTION
from comfy_extras.nodes_custom_sampler import RandomNoise, Noise_RandomNoise, BasicGuider, CFGGuider, SamplerCustomAdvanced
from comfy_extras.nodes_custom_sampler import BasicScheduler, BetaSamplingScheduler
from comfy_extras.nodes_custom_sampler import KSamplerSelect, SamplerLMS
from comfy_extras.nodes_sd3 import EmptySD3LatentImage
from comfy_extras.nodes_flux import FluxGuidance
from comfy.sd import VAE
import torch
from PIL import Image, ImageOps, ImageSequence
import numpy as np
import logging

def get_sigmas(model, scheduler, steps, denoise):
    get_basicscheduler = BasicScheduler()
    sigmas = get_basicscheduler.get_sigmas(model=model, scheduler=scheduler, steps=steps, denoise=denoise)[0]
    return sigmas

class AIO_Tuner_Pipe:
    @log_function_call
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model_type": (MODEL_TYPES, ),
                "guidance": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.01}),
                "sampler_name": (comfy.samplers.SAMPLER_NAMES, ),
                "scheduler": (comfy.samplers.SCHEDULER_NAMES, ),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "denoise": ("FLOAT", {"default": "1"}),
                "width": ("INT", {"default": 1024, "min": 16, "max": MAX_RESOLUTION, "step": 16}),
                "height": ("INT", {"default": 1024, "min": 16, "max": MAX_RESOLUTION, "step": 16}),
                "noise_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "debug": ("BOOLEAN", {"default": False}),
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
    RETURN_TYPES = ("SCA_PIPE", "CONDITIONING", "CONDITIONING", "CONDITIONING", "CONDITIONING", any)
    RETURN_NAMES = ("SCA_PIPE", "cond1", "cond2", "cond3", "cond4", "debug", )
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.ADVANCED.value

    FUNCTION = "determine_pipe_settings"

    def debugreturn(self, positive1=None, positive2=None, positive3=None, positive4=None):
        return (positive1, positive2, positive3, positive4)

    def determine_pipe_settings(self, model_type, guidance, sampler_name, scheduler, steps, denoise: float,
                                width, height, noise_seed, debug, model=None, positive=None, negative=None, vae=None, guider=None, sampler=None, sigmas=None,
                                extra_opts=None, samples=None):
        SCA_PIPE = []
        positive1 = "None"
        positive2 = "None"
        positive3 = "None"
        positive4 = "None"


        if isinstance(denoise, float):
            denoise = str(denoise)

        if ',' not in denoise:
            float_denoise = float(denoise)
            noise = Noise_RandomNoise(noise_seed)
            logger.info(f"Using random noise: {noise}")
            SCA_PIPE.append(noise)
        else:
            SCA_PIPE.append(noise_seed)

        if extra_opts == {}:
            extra_opts = None
        if extra_opts is not None and "cond" in extra_opts and len(positive) == 2:
            from ..nodes.cond import ApplyCondsExtraOpts
            get_applycondsextraopts = ApplyCondsExtraOpts()
            if "seed1" not in extra_opts:
                extra_opts5 = {"seed1": noise_seed}
                extra_opts = {**extra_opts, **extra_opts5}
            logger.info(f"Applying condition extra opts: {extra_opts}")
            positive = get_applycondsextraopts.apply_extra_opts(positive, extra_opts)[0]
            logger.info(f"Applied extra opts: {positive}")
            if debug:
                dbug = f"cond1: \n{positive}"
                positive1, positive2, positive3, positive4 = self.debugreturn(positive, positive2, positive3, positive4)
                return (SCA_PIPE, positive1, positive2, positive3, positive4, dbug)
        else:
            logger.info(f"Not applying condition extra opts")

        if guider is None:
            get_basicguider = BasicGuider()
            get_cfgguider = CFGGuider()
            if model_type == "FLUX":
                get_fluxguidance = FluxGuidance()
                if negative is None:
                    positive = get_fluxguidance.append(conditioning=positive, guidance=guidance)[0]
                    guider = get_basicguider.get_guider(model=model, conditioning=positive)[0]
                else:
                    positive = get_fluxguidance.append(conditioning=positive, guidance=guidance)[0]
                    negative = get_fluxguidance.append(conditioning=negative, guidance=guidance)[0]
                    guider = get_cfgguider.get_guider(model=model, positive=positive, negative=negative, cfg=1)[0]
            elif model_type == "SDXL":
                if extra_opts is not None and "schedule_cfg1" in extra_opts:
                    import importlib
                    module_name = 'custom_nodes.comfyui-inspire-pack.inspire.sampler_nodes'
                    inspire_pack_module = importlib.import_module(module_name)
                    ScheduledCFGGuider = inspire_pack_module.ScheduledCFGGuider
                    schedule_cfg1 = extra_opts["schedule_cfg1"]
                    from_cfg1 = extra_opts["from_cfg1"]
                    to_cfg1 = extra_opts["to_cfg1"]
                    logger.info(f"Using schedule_cfg:\n{schedule_cfg1}\n{from_cfg1}\n{to_cfg1}")
                    sigmas1 = get_sigmas(model=model, scheduler=scheduler, steps=steps, denoise=float_denoise)
                    logger.info(f"Using schedule_cfg sigmas:\n{sigmas1}")
                    if negative is None:
                        from nodes import ConditioningZeroOut
                        get_zero_out = ConditioningZeroOut()
                        neg_copy = positive.copy()
                        negative = get_zero_out.zero_out(neg_copy)[0]
                        logger.info(f"Using node's zeroed out conditioning:\n{negative}")
                    guider = ScheduledCFGGuider.get_guider(self, model=model, positive=positive, negative=negative, sigmas=sigmas1, from_cfg=from_cfg1, to_cfg=to_cfg1, schedule=schedule_cfg1)[0]
                    logger.info(f"Using schedule_cfg guider, sigmas:\n{guider}")

                elif negative is None and extra_opts is not None and "modify_pos_cfg1" in extra_opts:
                    noneg_cfg = extra_opts["modify_pos_cfg1"]
                    logger.info(f"Using external noneg_cfg: {noneg_cfg}")
                    from nodes import ConditioningZeroOut
                    get_zero_out = ConditioningZeroOut()
                    neg_copy = positive.copy()
                    negative = get_zero_out.zero_out(neg_copy)[0]
                    logger.info(f"Using node's zeroed out conditioning:\n{negative}")
                    guider = get_cfgguider.get_guider(model=model, positive=positive, negative=negative, cfg=noneg_cfg)[0]
                    logger.info(f"noneg with cfg guider:\n{guider}")
                elif negative is None:
                    guider = get_basicguider.get_guider(model=model, conditioning=positive)[0]
                    logger.info(f"Using node's guider: {guider}")
                else:
                    guider = get_cfgguider.get_guider(model=model, positive=positive, negative=negative, cfg=guidance)[0]
                    logger.info(f"Using node's guider: {guider}")
            else:
                if negative is None:
                    guider = get_basicguider.get_guider(model=model, conditioning=positive)[0]
                else:
                    guider = get_cfgguider.get_guider(model=model, positive=positive, negative=negative, cfg=guidance)[0]
                logger.info(f"FALLBACK!!!:\n{guider}")

            logger.info(f"Using node's guider: {guider}")
        else:
            logger.info(f"Using external guider: {guider}")

        SCA_PIPE.append(guider)


        if sampler is None:
            sampler = comfy.samplers.sampler_object(sampler_name)
            logger.info(f"Using node's sampler: {sampler}")
        else:
            logger.info(f"Using external sampler: {sampler}")
        SCA_PIPE.append(sampler)

        if ',' not in denoise:
            if sigmas is None:
                get_basicscheduler = BasicScheduler()
                sigmas = get_basicscheduler.get_sigmas(model=model, scheduler=scheduler, steps=steps, denoise=float_denoise)[0]
                logger.info(f"Using node's scheduler: {sigmas}")
            else:
                logger.info(f"Using external scheduler: {sigmas}")

            SCA_PIPE.append(sigmas)
        else:
            SCA_PIPE.append(scheduler)


        if samples is None:
            if extra_opts is not None:
                if "batch_size" in extra_opts:
                    batch_size = extra_opts["batch_size"]
                    if "width" in extra_opts and "height" in extra_opts:
                        width = extra_opts["width"]
                        height = extra_opts["height"]
                        logger.info(f"Using extra opts batch size: {batch_size}")
                        logger.info(f"Using extra opts width: {width}")
                        logger.info(f"Using extra opts height: {height}")
                    else:
                        logger.info(f"Using extra opts batch size: {batch_size}")
                else:
                    batch_size = 1
                    logger.info(f"Using default batch size: {batch_size}")
            else:
                batch_size = 1
                logger.info(f"Using default batch size: {batch_size}")

            if model_type == "FLUX":
                from comfy_extras.nodes_sd3 import EmptySD3LatentImage
                get_emptysd3latentimage = EmptySD3LatentImage()
                latent = get_emptysd3latentimage.generate(width, height, batch_size)[0]
                logger.info(f"Using node's FLUX latent generator: {latent["samples"].shape}")
            else:
                from nodes import EmptyLatentImage
                get_emptylatentimage = EmptyLatentImage()
                latent = get_emptylatentimage.generate(width, height, batch_size)[0]
                logger.info(f"Using node's SDXL latent generator: {latent["samples"].shape}")
        else:
            latent = samples
            logger.info(f"Using external latent: {latent["samples"].shape}")

        if extra_opts is None:
            extra_opts = {}

        SCA_PIPE.append(latent)
        SCA_PIPE.append(vae)
        SCA_PIPE.append(extra_opts)

        if ',' in denoise:
            SCA_PIPE.append(model)
            SCA_PIPE.append(denoise)
            SCA_PIPE.append(steps)

        return (SCA_PIPE, )


class SamplerCustomAdvanced_Pipe:
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

        if len(SCA_PIPE) == 10:
            noise_seed, guider, sampler, scheduler, latent, vae, extra_opts, model, denoise_schedule, steps = SCA_PIPE
            get_BasicScheduler = BasicScheduler()
        
            '''Thanks to https://github.com/syaofox/ComfyUI_fnodes'''
            denoise_values = [float(x.strip()) for x in denoise_schedule.split(',')]
            mask = latent.get('noise_mask', None)
            for i, denoise_value in enumerate(denoise_values):
                current_noise_seed = Noise_RandomNoise(noise_seed + i)
                current_steps = round(steps * denoise_value)
                current_sigmas = get_BasicScheduler.get_sigmas(model=model, scheduler=scheduler, steps=current_steps, denoise=denoise_value)[0]

                latent['noise_mask'] = mask
                out = get_samplercustomadvanced.sample(current_noise_seed, guider, sampler, current_sigmas, latent)
                latent = out[0]
        else:
            noise, guider, sampler, sigmas, latent, vae, extra_opts = SCA_PIPE
            out = get_samplercustomadvanced.sample(noise, guider, sampler, sigmas, latent)
        
        if extra_opts and "tile_size" in extra_opts:
            tile_size = extra_opts["tile_size"]
            overlap = extra_opts["overlap"]
            temporal_size = extra_opts["temporal_size"]
            temporal_overlap = extra_opts["temporal_overlap"]
            images = self.decode_tiled(vae, out[0], tile_size, overlap, temporal_size, temporal_overlap)
        else:
            images = self.decode(vae, out[0])

        out = out[0]

        return (images, out, )




'''
class FluxGuidance:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "conditioning": ("CONDITIONING", ),
            "guidance": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.1}),
            }}

    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "append"

    CATEGORY = "advanced/conditioning/flux"

    def append(self, conditioning, guidance):
        c = node_helpers.conditioning_set_values(conditioning, {"guidance": guidance})
        return (c, )
'''

