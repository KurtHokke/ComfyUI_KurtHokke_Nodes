from ..utils import any
from ..names import CATEGORY, MODEL_TYPES
import node_helpers
import comfy.samplers
from nodes import EmptyLatentImage, MAX_RESOLUTION
from comfy_extras.nodes_custom_sampler import RandomNoise, Noise_RandomNoise, BasicGuider, CFGGuider, SamplerCustomAdvanced
from comfy_extras.nodes_custom_sampler import BasicScheduler, BetaSamplingScheduler
from comfy_extras.nodes_custom_sampler import KSamplerSelect, SamplerLMS
from comfy_extras.nodes_sd3 import EmptySD3LatentImage
from comfy_extras.nodes_flux import FluxGuidance
import torch

class SamplerCustomAdvanced_Pipe:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "SCA_PIPE": (any, ),
            }
        }

    RETURN_TYPES = ("LATENT","LATENT")
    RETURN_NAMES = ("output", "denoised_output")

    FUNCTION = "get_sample"

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.TUNING.value

    def get_sample(self, SCA_PIPE=None):

        noise, guider, sampler, sigmas, latent = SCA_PIPE

        get_SamplerCustomAdvanced = SamplerCustomAdvanced()

        out = get_SamplerCustomAdvanced.sample(noise, guider, sampler, sigmas, latent_image=latent)
        out_denoised = out[1]
        out = out[0]

        return (out, out_denoised)


class stopipe:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "noise": ("NOISE", ),
                "guider": ("GUIDER", ),
                "sampler": ("SAMPLER", ),
                "sigmas": ("SIGMAS", ),
                "latent_image": ("LATENT", ),
            }
        }

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value
    RETURN_TYPES = (any,)

    FUNCTION = "execute"

    def execute(self, noise, guider, sampler, sigmas, latent_image):

        SCA_PIPE = []

        SCA_PIPE.append(noise)
        SCA_PIPE.append(guider)
        SCA_PIPE.append(sampler)
        SCA_PIPE.append(sigmas)
        SCA_PIPE.append(latent_image)

        return (SCA_PIPE,)


class AIO_Tuner:

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "positive": ("CONDITIONING",),
                "model_type": (MODEL_TYPES, ),
                "guidance": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.001}),
                "sampler": (comfy.samplers.SAMPLER_NAMES, ),
                "scheduler": (comfy.samplers.SCHEDULER_NAMES, ),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001}),
                "width": ("INT", {"default": 1024, "min": 16, "max": MAX_RESOLUTION, "step": 16}),
                "height": ("INT", {"default": 1024, "min": 16, "max": MAX_RESOLUTION, "step": 16}),
                "noise_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "negative": ("CONDITIONING",),
                "Scheduler_config": (any, ),
                "Sampler_config": (any, ),
            }
        }
    RETURN_TYPES = ("NOISE", "GUIDER", "SAMPLER", "SIGMAS", "LATENT")
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.TUNING.value

    FUNCTION = "determine_settings"

    def get_latent(self, model_type, width, height, batch_size=1):
        if model_type == "FLUX":
            latent = torch.zeros([batch_size, 16, height // 8, width // 8], device=self.device)
        elif model_type == "SDXL":
            latent = torch.zeros([batch_size, 4, height // 8, width // 8], device=self.device)
        else:
            latent = torch.zeros([batch_size, 4, height // 8, width // 8], device=self.device)
        return ({"samples":latent}, )


    def determine_settings(self, model, positive, model_type, guidance, sampler, scheduler, steps, denoise, 
                           width, height, noise_seed, negative=None, Scheduler_config=None, Sampler_config=None):
        #get_Noise_RandomNoise = Noise_RandomNoise()
        get_FluxGuidance = FluxGuidance()
        get_BasicGuider = BasicGuider()
        get_CFGGuider = CFGGuider()
        get_SamplerLMS = SamplerLMS()
        get_BetaSamplingScheduler = BetaSamplingScheduler()
        get_BasicScheduler = BasicScheduler()
        get_EmptyLatentImage = EmptyLatentImage()
        get_EmptySD3LatentImage = EmptySD3LatentImage()

        noise = Noise_RandomNoise(noise_seed)

        if model_type == "FLUX":
            if negative is None:
                positive = get_FluxGuidance.append(conditioning=positive, guidance=guidance)
                guider = get_BasicGuider.get_guider(model=model, conditioning=positive)[0]
            else:
                positive = get_FluxGuidance.append(conditioning=positive, guidance=guidance)
                negative = get_FluxGuidance.append(conditioning=negative, guidance=guidance)
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

        if Sampler_config is not None:
            if Sampler_config[0] == "LMS":
                SAMPLER, order = Sampler_config
                sampler = get_SamplerLMS.get_sampler(order=order)
            else:
                SAMPLER, *SAMPLER_opts = Sampler_config
                sampler = comfy.samplers.sampler_object(sampler)
                if len(SAMPLER_opts) == 1:
                    print(f"!!!!! Sampler_config got unexpected input: {SAMPLER}, {SAMPLER_opts[0]} !!!!!")
                elif len(SAMPLER_opts) > 1:
                    SAMPLER_opts_str = ', '.join(map(str, SAMPLER_opts))
                    print(f"!!!!! Sampler_config got unexpected input: {SAMPLER}, {SAMPLER_opts_str} !!!!!")
                else:
                    print(f"!!!!! Sampler_config got unexpected input: {SAMPLER} !!!!!")
                print(f"!!!!! Using {sampler} instead !!!!!")
        else:
            sampler = comfy.samplers.sampler_object(sampler)
        
        if Scheduler_config is not None:
            if Scheduler_config[0] == "BETA":
                SCHEDULER, alpha, beta = Scheduler_config 
                sigmas = get_BetaSamplingScheduler.get_sigmas(model=model, steps=steps, alpha=alpha, beta=beta)[0]
            else:
                SCHEDULER, *SCHEDULER_opts = Scheduler_config
                sigmas = get_BasicScheduler.get_sigmas(model=model, scheduler=scheduler, steps=steps, denoise=denoise)[0]
                if len(SCHEDULER_opts) == 1:
                    print(f"!!!!! Sampler_config got unexpected input: {SCHEDULER}, {SCHEDULER_opts[0]} !!!!!")
                elif len(SCHEDULER_opts) > 1:
                    SCHEDULER_opts_str = ', '.join(map(str, SCHEDULER_opts))
                    print(f"!!!!! Sampler_config got unexpected input: {SCHEDULER}, {SCHEDULER_opts_str} !!!!!")
                else:
                    print(f"!!!!! Sampler_config got unexpected input: {SCHEDULER} !!!!!")
                print(f"!!!!! Using {scheduler} instead !!!!!")
        else:
            sigmas = get_BasicScheduler.get_sigmas(model=model, scheduler=scheduler, steps=steps, denoise=denoise)[0]

        latent = self.get_latent(model_type, width=width, height=height, batch_size=1)[0]



        return(noise, guider, sampler, sigmas, latent)


class AIO_Tuner_Pipe:

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "positive": ("CONDITIONING",),
                "model_type": (MODEL_TYPES, ),
                "guidance": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.001}),
                "sampler": (comfy.samplers.SAMPLER_NAMES, ),
                "scheduler": (comfy.samplers.SCHEDULER_NAMES, ),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001}),
                "width": ("INT", {"default": 1024, "min": 16, "max": MAX_RESOLUTION, "step": 16}),
                "height": ("INT", {"default": 1024, "min": 16, "max": MAX_RESOLUTION, "step": 16}),
                "noise_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "negative": ("CONDITIONING",),
                "Scheduler_config": (any, ),
                "Sampler_config": (any, ),
            }
        }
    RETURN_TYPES = (any,)
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.TUNING.value

    FUNCTION = "determine_pipe_settings"

    def get_latent(self, model_type, width, height, batch_size=1):
        if model_type == "FLUX":
            latent = torch.zeros([batch_size, 16, height // 8, width // 8], device=self.device)
        elif model_type == "SDXL":
            latent = torch.zeros([batch_size, 4, height // 8, width // 8], device=self.device)
        else:
            latent = torch.zeros([batch_size, 4, height // 8, width // 8], device=self.device)
        return ({"samples":latent}, )


    def determine_pipe_settings(self, model, positive, model_type, guidance, sampler, scheduler, steps, denoise, 
                                width, height, noise_seed, negative=None, Scheduler_config=None, Sampler_config=None):
        #get_Noise_RandomNoise = Noise_RandomNoise()
        get_FluxGuidance = FluxGuidance()
        get_BasicGuider = BasicGuider()
        get_CFGGuider = CFGGuider()
        get_SamplerLMS = SamplerLMS()
        get_BetaSamplingScheduler = BetaSamplingScheduler()
        get_BasicScheduler = BasicScheduler()
        get_EmptyLatentImage = EmptyLatentImage()
        get_EmptySD3LatentImage = EmptySD3LatentImage()

        noise = Noise_RandomNoise(noise_seed)

        if model_type == "FLUX":
            if negative is None:
                positive = get_FluxGuidance.append(conditioning=positive, guidance=guidance)
                guider = get_BasicGuider.get_guider(model=model, conditioning=positive)[0]
            else:
                positive = get_FluxGuidance.append(conditioning=positive, guidance=guidance)
                negative = get_FluxGuidance.append(conditioning=negative, guidance=guidance)
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

        if Sampler_config is not None:
            if Sampler_config[0] == "LMS":
                SAMPLER, order = Sampler_config
                sampler = get_SamplerLMS.get_sampler(order=order)
            else:
                SAMPLER, *SAMPLER_opts = Sampler_config
                sampler = comfy.samplers.sampler_object(sampler)
                if len(SAMPLER_opts) == 1:
                    print(f"!!!!! Sampler_config got unexpected input: {SAMPLER}, {SAMPLER_opts[0]} !!!!!")
                elif len(SAMPLER_opts) > 1:
                    SAMPLER_opts_str = ', '.join(map(str, SAMPLER_opts))
                    print(f"!!!!! Sampler_config got unexpected input: {SAMPLER}, {SAMPLER_opts_str} !!!!!")
                else:
                    print(f"!!!!! Sampler_config got unexpected input: {SAMPLER} !!!!!")
                print(f"!!!!! Using {sampler} instead !!!!!")
        else:
            sampler = comfy.samplers.sampler_object(sampler)
        
        if Scheduler_config is not None:
            if Scheduler_config[0] == "BETA":
                SCHEDULER, alpha, beta = Scheduler_config 
                sigmas = get_BetaSamplingScheduler.get_sigmas(model=model, steps=steps, alpha=alpha, beta=beta)[0]
            else:
                SCHEDULER, *SCHEDULER_opts = Scheduler_config
                sigmas = get_BasicScheduler.get_sigmas(model=model, scheduler=scheduler, steps=steps, denoise=denoise)[0]
                if len(SCHEDULER_opts) == 1:
                    print(f"!!!!! Sampler_config got unexpected input: {SCHEDULER}, {SCHEDULER_opts[0]} !!!!!")
                elif len(SCHEDULER_opts) > 1:
                    SCHEDULER_opts_str = ', '.join(map(str, SCHEDULER_opts))
                    print(f"!!!!! Sampler_config got unexpected input: {SCHEDULER}, {SCHEDULER_opts_str} !!!!!")
                else:
                    print(f"!!!!! Sampler_config got unexpected input: {SCHEDULER} !!!!!")
                print(f"!!!!! Using {scheduler} instead !!!!!")
        else:
            sigmas = get_BasicScheduler.get_sigmas(model=model, scheduler=scheduler, steps=steps, denoise=denoise)[0]

        latent = self.get_latent(model_type, width=width, height=height, batch_size=1)[0]

        SCA_PIPE = []

        SCA_PIPE.append(noise)
        SCA_PIPE.append(guider)
        SCA_PIPE.append(sampler)
        SCA_PIPE.append(sigmas)
        SCA_PIPE.append(latent)

        return (SCA_PIPE,)


class LMS_Config:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "order": ("INT", {"default": 4, "min": 1, "max": 100}),
            }
        }
    RETURN_TYPES = ("Sampler_config",)
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.TUNING.value

    FUNCTION = "get_LMS_Config"

    def get_LMS_Config(self, order):
        SAMPLER = "LMS"
        Sampler_config.append(LMS)
        Sampler_config.append(order)
        #sampler = comfy.samplers.ksampler("lms", {"order": order})
        return (Sampler_config, )

class Beta_Config:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "alpha": ("FLOAT", {"default": 0.6, "min": -50.0, "max": 50.0, "step":0.001, "round": False}),
                "beta": ("FLOAT", {"default": 0.6, "min": -50.0, "max": 50.0, "step":0.001, "round": False}),
            }
        }
    RETURN_TYPES = ("Scheduler_config",)
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.TUNING.value

    FUNCTION = "get_Beta_Config"

    def get_Beta_Config(self, alpha, beta):
        SCHEDULER = "BETA"
        Scheduler_config.append(BETA)
        Scheduler_config.append(alpha)
        Scheduler_config.append(beta)
        return(Scheduler_config, )

class BasicAdvScheduler:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "scheduler": (comfy.samplers.SCHEDULER_NAMES, ),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001}),
            },
            "optional": {
                "Scheduler_config": (any, )
            }
        }
    RETURN_TYPES = ("SIGMAS",)
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.TUNING.value

    FUNCTION = "determine_sigmas"

    def determine_sigmas(self, model, scheduler, steps, denoise, Scheduler_config=None):
        total_steps = steps
        if denoise < 1.0:
            if denoise <= 0.0:
                return (torch.FloatTensor([]),)
            total_steps = int(steps/denoise)

        if Scheduler_config is not None:
            if Scheduler_config[0] == "BETA":
                BETA, alpha, beta = Scheduler_config 
                sigmas = BetaSamplingScheduler.get_sigmas(model=model, steps=steps, alpha=alpha, beta=beta)
                return(sigmas, )

        sigmas = comfy.samplers.calculate_sigmas(model.get_model_object("model_sampling"), scheduler, total_steps).cpu()
        sigmas = sigmas[-(steps + 1):]
        return (sigmas, )



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

