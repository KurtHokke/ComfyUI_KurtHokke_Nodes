from khn.loggers import get_logger
from comfy.samplers import CFGGuider, sampler_object
from comfy.comfy_types import IO, InputTypeDict
from comfy_extras.nodes_flux import CLIPTextEncodeFlux, FluxGuidance
from comfy_extras.nodes_custom_sampler import BasicScheduler, BasicGuider, CFGGuider, Noise_RandomNoise
from nodes import CLIPTextEncode, ConditioningZeroOut, EmptyLatentImage
from comfy_extras.nodes_sd3 import EmptySD3LatentImage
import torch

logger, decoDebug = get_logger("all")

@decoDebug
class SampleAssembler:
    def __init__(self, sca_dict):
        self.sca_dict = sca_dict.copy()
        self.basic_scheduler = BasicScheduler()
        self._start(init=True)

    def _start(self, init=False):
        if init:
            self._vaeattr()
        self._get_guider()
        self._get_sampler()
        self._get_sigmas()
        self._get_latent()
        self._assemble_pipe()

    def _vaeattr(self):
        vae = self.sca_dict["vae"]
        if vae is not None and hasattr(vae, "latent_channels"):
            self.latent_ch = vae.latent_channels
            if self.latent_ch == 16:
                self._instance("fluxclip", "fluxguidance", "fluxlatent")
            else:
                self.latent_ch = 4
                self._instance("sdclip", "sdlatent")
            self.vae = vae

    def _instance(self, *args):
        for x in args:
            if x == "basicguider" and not hasattr(self, "basicguider"):
                self.basicguider = BasicGuider()
            elif x == "fluxclip" and not hasattr(self, "fluxclip"):
                self.fluxclip = CLIPTextEncodeFlux()
            elif x == "fluxguidance" and not hasattr(self, "fluxguidance"):
                self.fluxguidance = FluxGuidance()
            elif x == "fluxlatent" and not hasattr(self, "fluxlatent"):
                self.fluxlatent = EmptySD3LatentImage()
            elif x == "cfgguider" and not hasattr(self, "cfgguider"):
                self.cfgguider = CFGGuider()
            elif x == "sdclip" and not hasattr(self, "sdclip"):
                self.sdclip = CLIPTextEncode()
            elif x == "cond_zero_out" and not hasattr(self, "cond_zero_out"):
                self.cond_zero_out = ConditioningZeroOut()
            elif x == "sdlatent" and not hasattr(self, "sdlatent"):
                self.sdlatent = EmptyLatentImage()
            else:
                logger.info(f"Error: _instance() {x}")
                return None

    def update(self, sca_dict, noise_seed):
        noise = Noise_RandomNoise(noise_seed)
        if sca_dict == self.sca_dict:
            return {**self.sca_pipe, "noise": noise}
        else:
            is_changed = False
            prev_sca_dict = self.sca_dict.copy()
            self.sca_dict = sca_dict.copy()
            if sca_dict["vae"] != prev_sca_dict["vae"]:
                prev_latent_ch = self.latent_ch
                latent_ch = sca_dict["vae"].latent_channels
                if prev_latent_ch != latent_ch:
                    self._start(init=True)
                    return {**self.sca_pipe, "noise": noise}
            if sca_dict["model"] != prev_sca_dict["model"] or sca_dict["clip"] != prev_sca_dict["clip"] or sca_dict["pos"] != prev_sca_dict["pos"] or sca_dict["neg"] != prev_sca_dict["neg"]:
                self._get_guider()
                is_changed = True
            if sca_dict["scheduler"] != prev_sca_dict["scheduler"] or sca_dict["denoise"] != prev_sca_dict["denoise"] or sca_dict["steps"] != prev_sca_dict["steps"]:
                self._get_sigmas()
                is_changed = True
            if sca_dict["width"] != prev_sca_dict["width"] or sca_dict["height"] != prev_sca_dict["height"]:
                self._get_latent()
                is_changed = True
            if sca_dict["sampler_name"] != prev_sca_dict["sampler_name"]:
                self._get_sampler()
                is_changed = True
            if not is_changed:
                self._start()
                return {**self.sca_pipe, "noise": noise}
            self._assemble_pipe()
            return {**self.sca_pipe, "noise": noise}

    def _get_guider(self):
        model = self.sca_dict["model"]
        clip = self.sca_dict["clip"]
        pos = self.sca_dict["pos"]
        neg = self.sca_dict["neg"]
        cfg_guid = self.sca_dict["cfg_guid"]
        if self.latent_ch == 16:
            pos_cond = self.fluxclip.encode(clip=clip, clip_l=pos[1], t5xxl=pos[0], guidance=cfg_guid)[0]
            pos_cond = self.fluxguidance.append(conditioning=pos_cond, guidance=cfg_guid)[0]
            if neg is None:
                self._instance("basicguider")
                self.guider = self.basicguider.get_guider(model=model, conditioning=pos_cond)[0]
            else:
                self._instance("cfgguider")
                neg_cond = self.sdclip.encode(clip=clip, text=neg[0])[0]


        else:
            pos_cond = self.sdclip.encode(clip=clip, text=pos[0])[0]
            if neg is None:
                if "skip_emptyneg" in self.sca_dict["extra_opts"]:
                    neg_copy = pos_cond.copy()
                neg_cond = self.cond_zero_out.zero_out(conditioning=neg_copy)[0]
                self.guider = self.cfgguider.get_guider(model=model, positive=pos_cond, negative=neg_cond, cfg=cfg_guid)[0]

            elif neg is not None:
                neg_cond = self.sdclip.encode(clip=clip, text=neg[0])[0]
                self.guider = self.cfgguider.get_guider(model=model, positive=pos_cond, negative=neg_cond, cfg=cfg_guid)[0]

            else:
                logger.info("Error: get_guider()")

    def _get_sigmas(self):
        model = self.sca_dict["model"]
        scheduler = self.sca_dict["scheduler"]
        denoise = self.sca_dict["denoise"]
        steps = self.sca_dict["steps"]
        self.sigmas = self.basic_scheduler.get_sigmas(model=model, scheduler=scheduler, steps=steps, denoise=denoise)[0]

    def _get_sampler(self):
        sampler_name = self.sca_dict["sampler_name"]
        self.sampler = sampler_object(sampler_name)

    def _get_latent(self):
        width = self.sca_dict["width"]
        height = self.sca_dict["height"]
        if self.latent_ch == 16:
            self.latent_image = self.fluxlatent.generate(width, height, 1)[0]
        else:
            self.latent_image = self.sdlatent.generate(width, height, 1)[0]

    def _assemble_pipe(self):
        self.sca_pipe = {
            "guider": self.guider,
            "sampler": self.sampler,
            "sigmas": self.sigmas,
            "samples": self.latent_image,
            "vae": self.vae,
        }