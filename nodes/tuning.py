from ..utils import CATEGORY, MODEL_TYPES
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
from .cond import ConditioningProcessor

'''
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
                "debug": ("BOOLEAN", {"default": False}),
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
    RETURN_TYPES = ("SCA_PIPE", "CONDITIONING",)
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.ADVANCED.value

    FUNCTION = "determine_pipe_settings"

    def get_latent(self, model_type, width, height, batch_size=1):
        if model_type == "FLUX":
            latent = torch.zeros([batch_size, 16, height // 8, width // 8], device=self.device)
        elif model_type == "SDXL":
            latent = torch.zeros([batch_size, 4, height // 8, width // 8], device=self.device)
        else:
            latent = torch.zeros([batch_size, 4, height // 8, width // 8], device=self.device)
        return ({"samples":latent}, )



    def determine_pipe_settings(self, model, positive, model_type, guidance, sampler_name, scheduler, steps, denoise: float,
                                width, height, noise_seed, debug, negative=None, vae=None, guider=None, sampler=None, sigmas=None,
                                extra_opts=None, samples=None):
        SCA_PIPE = []

        if isinstance(denoise, float):
            denoise = str(denoise)
        if ',' not in denoise:
            float_denoise = float(denoise)
            noise = Noise_RandomNoise(noise_seed)

            SCA_PIPE.append(noise)
        else:
            SCA_PIPE.append(noise_seed)

        print(len(positive))
        print(len(positive))

        if extra_opts == {}:
            extra_opts = None
        if extra_opts is not None:
            process_conds = ConditioningProcessor()

            try:
                affected_conds1 = [int(cond.strip()) - 1 for cond in extra_opts["affected_conds1"].split(",")]
                if "affected_conds2" in extra_opts:
                    affected_conds2 = [int(cond.strip()) - 1 for cond in extra_opts["affected_conds2"].split(",")]
                else:
                    affected_conds2 = None

                if "combine1" in extra_opts:
                    positive = process_conds.combine(positive[affected_conds1[0]], positive[affected_conds1[1]])[0]

                elif "concat1" in extra_opts:
                    if extra_opts["direction1"] == '<':
                        positive = process_conds.concat(positive[affected_conds1[0]], positive[affected_conds1[1]])
                    elif extra_opts["direction1"] == '>':
                        positive = process_conds.concat(positive[affected_conds1[1]], positive[affected_conds1[0]])[0]

                elif "average1" in extra_opts:
                    if extra_opts["direction1"] == '<':
                        positive = process_conds.addWeighted(positive[affected_conds1[0]], positive[affected_conds1[1]], extra_opts["average_strength1"])[0]
                    elif extra_opts["direction1"] == '>':
                        positive = process_conds.addWeighted(positive[affected_conds1[1]], positive[affected_conds1[0]], extra_opts["average_strength1"])[0]

                if affected_conds2 is not None:
                    if "combine2" in extra_opts:
                        positive = process_conds.combine(positive[affected_conds2[0]], positive[affected_conds2[1]])[0]

                    elif "concat2" in extra_opts:
                        if extra_opts["direction2"] == '<':
                            positive = process_conds.concat(positive[affected_conds2[0]], positive[affected_conds2[1]])[0]
                        elif extra_opts["direction2"] == '>':
                            positive = process_conds.concat(positive[affected_conds2[1]], positive[affected_conds2[0]])[0]

                    elif "average2" in extra_opts:
                        if extra_opts["direction2"] == '<':
                            positive = process_conds.addWeighted(positive[affected_conds2[0]], positive[affected_conds2[1]], extra_opts["average_strength2"])[0]
                        elif extra_opts["direction2"] == '>':
                            positive = process_conds.addWeighted(positive[affected_conds2[1]], positive[affected_conds2[0]], extra_opts["average_strength2"])[0]



            except Exception as e:
                print(f"Error while processing extra_opts: {e}")
                pass
        else:
            positive = positive[0]
        def flatten(nested_list):
            result = []
            for sublist in nested_list:
                for item in sublist:
                    result.append(item)
            return result
        positive = flatten(positive)
        if debug:
            return (SCA_PIPE, positive, )
        if guider is None:
            get_BasicGuider = BasicGuider()
            get_CFGGuider = CFGGuider()
            if model_type == "FLUX":
                get_FluxGuidance = FluxGuidance()
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
                get_BasicScheduler = BasicScheduler()
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

        return (SCA_PIPE, positive)
'''

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
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.ADVANCED.value

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
                    guider = get_BasicGuider.get_guider(model=model, conditioning=positive)
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

