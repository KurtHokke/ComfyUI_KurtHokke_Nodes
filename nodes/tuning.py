from ..utils import CATEGORY, MODEL_TYPES, CONCAT_WHERE, any
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


class AIO_Tuner_Pipe:

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL", ),
                "positive": ("CONDITIONING", ),
                "model_type": (MODEL_TYPES, ),
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
    CATEGORY = CATEGORY.MAIN.value + "/Advanced"

    FUNCTION = "determine_pipe_settings"

    def addWeighted(self, conditioning_to, conditioning_from, conditioning_to_strength):
        out = []
        if len(conditioning_from) > 1:
            logging.warning("Warning: ConditioningAverage conditioning_from contains more than 1 cond, only the first one will actually be applied to conditioning_to.")
        cond_from = conditioning_from[0][0]
        pooled_output_from = conditioning_from[0][1].get("pooled_output", None)

        for i in range(len(conditioning_to)):
            t1 = conditioning_to[i][0]
            pooled_output_to = conditioning_to[i][1].get("pooled_output", pooled_output_from)
            t0 = cond_from[:,:t1.shape[1]]
            if t0.shape[1] < t1.shape[1]:
                t0 = torch.cat([t0] + [torch.zeros((1, (t1.shape[1] - t0.shape[1]), t1.shape[2]))], dim=1)

            tw = torch.mul(t1, conditioning_to_strength) + torch.mul(t0, (1.0 - conditioning_to_strength))
            t_to = conditioning_to[i][1].copy()
            if pooled_output_from is not None and pooled_output_to is not None:
                t_to["pooled_output"] = torch.mul(pooled_output_to, conditioning_to_strength) + torch.mul(pooled_output_from, (1.0 - conditioning_to_strength))
            elif pooled_output_from is not None:
                t_to["pooled_output"] = pooled_output_from

            n = [tw, t_to]
            out.append(n)
        return (out, )

    def concat(self, conditioning_to, conditioning_from):
        out = []
        print(conditioning_from)
        print(conditioning_to)
        if len(conditioning_from) > 1:
            logging.warning("Warning: ConditioningConcat conditioning_from contains more than 1 cond, only the first one will actually be applied to conditioning_to.")

        cond_from = conditioning_from[0][0]
        print(cond_from)
        for i in range(len(conditioning_to)):
            t1 = conditioning_to[i][0]
            print(t1)
            tw = torch.cat((t1, cond_from),1)
            print(tw)
            n = [tw, conditioning_to[i][1].copy()]
            print(n)
            out.append(n)
            print(out)
        return (out, )

    def combine(self, conditioning):
        if len(conditioning) > 1:
        # Initialize the combined result (assuming tuples for this example)
            combined = conditioning[0]

            # Loop through remaining items and combine them
            for item in conditioning[1:]:
                # Depending on your requirements, you can define the combination logic
                combined += item

            return (combined,)

    def get_latent(self, model_type, width, height, batch_size=1):
        if model_type == "FLUX":
            latent = torch.zeros([batch_size, 16, height // 8, width // 8], device=self.device)
        elif model_type == "SDXL":
            latent = torch.zeros([batch_size, 4, height // 8, width // 8], device=self.device)
        else:
            latent = torch.zeros([batch_size, 4, height // 8, width // 8], device=self.device)
        return ({"samples":latent}, )

    def determine_pipe_settings(self, model, positive, model_type, guidance, sampler_name, scheduler, steps, denoise: float,
                                width, height, noise_seed, negative=None, vae=None, guider=None, sampler=None, sigmas=None,
                                extra_opts=None, samples=None):
        get_FluxGuidance = FluxGuidance()
        get_BasicGuider = BasicGuider()
        get_CFGGuider = CFGGuider()
        get_BasicScheduler = BasicScheduler()


        SCA_PIPE = []

        if isinstance(denoise, float):
        # Convert float to string for consistent checking
            denoise = str(denoise)


        if ',' not in denoise:
            float_denoise = float(denoise)
            noise = Noise_RandomNoise(noise_seed)

            SCA_PIPE.append(noise)
        else:
            SCA_PIPE.append(noise_seed)

        print(len(positive))
        print(len(positive))
        print(len(positive))
        print(len(positive))

        if extra_opts is not None:
            if "combine" in extra_opts:
                positive = self.combine(conditioning=positive)[0]
            elif "concat" in extra_opts:
                if extra_opts["concat_where"] == '<':
                    positive = self.concat(conditioning_to=positive[0], conditioning_from=positive[1])[0]
                elif extra_opts["concat_where"] == '>':
                    positive = self.concat(conditioning_to=positive[1], conditioning_from=positive[0])[0]
            elif "average" in extra_opts:
                positive = self.addWeighted(conditioning_to=positive[0], conditioning_from=positive[1], conditioning_to_strength=extra_opts["average_strength"])[0]
            else:
                positive = positive[0]
        else:
            positive = positive[0]

        if guider is None:
            if model_type == "FLUX":
                if negative is None:
                    positive = get_FluxGuidance.append(conditioning=positive, guidance=guidance)[0]
                    guider = get_BasicGuider.get_guider(model=model, conditioning=positive)[0]
                else:
                    positive = get_FluxGuidance.append(conditioning=positive, guidance=guidance)[0]
                    negative = get_FluxGuidance.append(conditioning=negative, guidance=guidance)[0]
                    guider = get_CFGGuider.get_guider(model=model, positive=positive, negative=negative, cfg=1)[0]
            elif model_type == "SDXL":
                if negative is None:
                    guider = get_BasicGuider.get_guider(model=model, conditioning=positive)[0]
                else:
                    guider = get_CFGGuider.get_guider(model=model, positive=positive, negative=negative, cfg=guidance)[0]
            else:
                if negative is None:
                    guider = get_BasicGuider.get_guider(model=model, conditioning=positive)[0]
                else:
                    guider = get_CFGGuider.get_guider(model=model, positive=positive, negative=negative, cfg=guidance)[0]
        
        SCA_PIPE.append(guider)


        if sampler is None:
            sampler = comfy.samplers.sampler_object(sampler_name)

        SCA_PIPE.append(sampler)
        

        if ',' not in denoise:
            if sigmas is None:
                sigmas = get_BasicScheduler.get_sigmas(model=model, scheduler=scheduler, steps=steps, denoise=float_denoise)[0]

            SCA_PIPE.append(sigmas)
        else:
            SCA_PIPE.append(scheduler)


        if samples is None:
            latent = self.get_latent(model_type, width=width, height=height, batch_size=1)[0]
        else:
            latent = samples

        SCA_PIPE.append(latent)
        SCA_PIPE.append(vae)
        SCA_PIPE.append(extra_opts)

        if ',' in denoise:
            SCA_PIPE.append(model)
            SCA_PIPE.append(denoise)
            SCA_PIPE.append(steps)

        return (SCA_PIPE, )

class MergeExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "extra_opts1": ("EXTRA_OPTS", ),
            },
            "optional": {
                "extra_opts2": ("EXTRA_OPTS", ),
            }
        }
    RETURN_TYPES = ("EXTRA_OPTS", )
    RETURN_NAMES = ("extra_opts", )
    FUNCTION = "merge_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + "/Advanced"

    def merge_extra_opts(self, extra_opts1=None, extra_opts2=None):
        if extra_opts1 is None:
            extra_opts1 = {}
        if extra_opts2 is None:
            extra_opts2 = {}
        extra_opts = {**extra_opts1, **extra_opts2}
        return (extra_opts, )


class COND_ExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"cond_n": ("STRING", {"default": "1,2"}),
                             "combine": ("BOOLEAN", {"default": True, "label_on": "On", "label_off": "Off"}),
                             "concat": ("BOOLEAN", {"default": False, "label_on": "On", "label_off": "Off"}),
                             "concat_where": (CONCAT_WHERE, ),
                             "average": ("BOOLEAN", {"default": False, "label_on": "On", "label_off": "Off"}),
                             "average_strength": ("FLOAT", {"default": 0.500, "min": 0.000, "max": 1.000, "step": 0.001}),
                            }
                }
    RETURN_TYPES = ("EXTRA_OPTS", )
    RETURN_NAMES = ("extra_opts", )
    FUNCTION = "pack_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + "/Advanced"

    def pack_extra_opts(self, cond_n, combine, average, average_strength, concat, concat_where):
        extra_opts1 = {"cond_n": cond_n}
        if combine:
            extra_opts2 = {"combine": combine}
        else:
            extra_opts2 = {}

        if average:
            extra_opts3 = {"average": average}
            extra_opts4 = {"average_strength": average_strength}
        else:
            extra_opts3 = {}
            extra_opts4 = {}
        if concat:
            extra_opts5 = {"concat": concat}
            extra_opts6 = {"concat_where": concat_where}
        else:
            extra_opts5 = {}
            extra_opts6 = {}
        extra_opts = {**extra_opts1, **extra_opts2, **extra_opts3, **extra_opts4, **extra_opts5, **extra_opts6}
        return (extra_opts, )


class VAE_ExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"switch": ("BOOLEAN", {"default": True, "label_on": "On", "label_off": "Off"}),
                             "tile_size": ("INT", {"default": 512, "min": 64, "max": 4096, "step": 32}),
                             "overlap": ("INT", {"default": 64, "min": 0, "max": 4096, "step": 32}),
                             "temporal_size": ("INT", {"default": 64, "min": 8, "max": 4096, "step": 4, "tooltip": "Only used for video VAEs: Amount of frames to decode at a time."}),
                             "temporal_overlap": ("INT", {"default": 8, "min": 4, "max": 4096, "step": 4, "tooltip": "Only used for video VAEs: Amount of frames to overlap."}),
                            }}
    RETURN_TYPES = ("EXTRA_OPTS", )
    RETURN_NAMES = ("extra_opts", )
    FUNCTION = "pack_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + "/Advanced"

    def pack_extra_opts(self, switch, tile_size, overlap, temporal_size, temporal_overlap):
        if switch:
            extra_opts = {"tile_size": tile_size, "overlap": overlap, "temporal_size": temporal_size, "temporal_overlap": temporal_overlap}
        else:
            extra_opts = {}
        return (extra_opts, )

class VAEDecodeTiled:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"samples": ("LATENT", ), "vae": ("VAE", ),
                             "tile_size": ("INT", {"default": 512, "min": 64, "max": 4096, "step": 32}),
                             "overlap": ("INT", {"default": 64, "min": 0, "max": 4096, "step": 32}),
                             "temporal_size": ("INT", {"default": 64, "min": 8, "max": 4096, "step": 4, "tooltip": "Only used for video VAEs: Amount of frames to decode at a time."}),
                             "temporal_overlap": ("INT", {"default": 8, "min": 4, "max": 4096, "step": 4, "tooltip": "Only used for video VAEs: Amount of frames to overlap."}),
                            }}
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "decode"

    CATEGORY = "_for_testing"

    def decode(self, vae, samples, tile_size, overlap=64, temporal_size=64, temporal_overlap=8):
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
        images = vae.decode_tiled(samples["samples"], tile_x=tile_size // compression, tile_y=tile_size // compression, overlap=overlap // compression, tile_t=temporal_size, overlap_t=temporal_overlap)
        if len(images.shape) == 5: #Combine batches
            images = images.reshape(-1, images.shape[-3], images.shape[-2], images.shape[-1])
        return (images, )

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

    CATEGORY = CATEGORY.MAIN.value + "/Advanced"

    def decode(self, vae, samples):
        images = vae.decode(samples["samples"])[0]
        # print(i)  # To check what `i` is
        # print(type(i))  # To see its type
        # print(i.shape)

        if len(images.shape) == 5: #Combine batches
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
        if len(images.shape) == 5: #Combine batches
            images = images.reshape(-1, images.shape[-3], images.shape[-2], images.shape[-1])
        return (images, )

    def get_sample(self, SCA_PIPE=None):
        
        get_SamplerCustomAdvanced = SamplerCustomAdvanced()

        if len(SCA_PIPE) == 7:
            noise, guider, sampler, sigmas, latent, vae, extra_opts = SCA_PIPE
            out = get_SamplerCustomAdvanced.sample(noise, guider, sampler, sigmas, latent)
        elif len(SCA_PIPE) == 10:
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
                out = get_SamplerCustomAdvanced.sample(current_noise_seed, guider, sampler, current_sigmas, latent)
                latent = out[0]
        if "tile_size" in extra_opts:
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

