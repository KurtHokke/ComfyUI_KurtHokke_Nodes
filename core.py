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
        self._get_dicts = self._update__get_dicts()
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
            _get_dicts = self._update__get_dicts()
            if sca_dict["vae"] != prev_sca_dict["vae"]:
                prev_latent_ch = self.latent_ch
                latent_ch = sca_dict["vae"].latent_channels
                if prev_latent_ch != latent_ch:
                    self._update("ALL", changed=True)
                    return {**self.sca_pipe, "noise": noise}
            if _get_dicts["guider_dict"] != self._get_dicts["guider_dict"]:
                current_guider_dict_nocfg = {k: v for k, v in _get_dicts["guider_dict"].items() if k != "cfg_guid"}
                prev_guider_dict_nocfg = {k: v for k, v in self._get_dicts["guider_dict"].items() if k != "cfg_guid"}
                logger.debug(f"current_guider_dict_nocfg: {current_guider_dict_nocfg}")
                logger.debug(f"_get_dicts['guider_dict']: {_get_dicts['guider_dict']}")
                logger.debug(f"prev_guider_dict_nocfg: {prev_guider_dict_nocfg}")
                logger.debug(f"self._get_dicts['guider_dict']: {self._get_dicts['guider_dict']}")
                if current_guider_dict_nocfg == prev_guider_dict_nocfg:
                    self._update("guider", changed=self.sca_dict["cfg_guid"])
                else:
                    self._update("guider")
                is_changed = True

            if _get_dicts["sigmas_dict"] != self._get_dicts["sigmas_dict"]:
                self._update("sigmas")
                is_changed = True

            if _get_dicts["sampler_dict"] != self._get_dicts["sampler_dict"]:
                self._update("sampler")
                is_changed = True

            if _get_dicts["latent_dict"] != self._get_dicts["latent_dict"]:
                self._update("latent")
                is_changed = True

            if not is_changed:
                self._update("ALL", changed=False)

            return {**self.sca_pipe, "noise": noise}

    def _update(self, *args, changed="ALL"):
        for x in args:
            if x == "guider":
                self._get_guider(changed)
            elif x == "sigmas":
                self._get_sigmas(changed)
            elif x == "sampler":
                self._get_sampler(changed)
            elif x == "latent":
                self._get_latent(changed)
            elif x == "ALL":
                logger.info(f"UPDATING ALL!!!!")
                self._start(init=changed)
                return
        self._assemble_pipe()

    def _guider(self, model, cfg_guid, neg=False):
        if neg:
            self._instance("cfgguider")
            self.guider = self.cfgguider.get_guider(model=model, positive=self.pos_cond, negative=self.neg_cond, cfg=cfg_guid)[0]
        else:
            self._instance("basicguider")
            self.guider = self.basicguider.get_guider(model=model, conditioning=self.pos_cond)[0]

    def _get_guider(self, changed="ALL"):
        model, clip, pos, neg, cfg_guid = self._getitem(self._get_dicts["guider_dict"])
        if self.latent_ch == 16:
            self.pos_cond = self.fluxclip.encode(clip=clip, clip_l=pos[1], t5xxl=pos[0], guidance=cfg_guid)[0]
            self.pos_cond = self.fluxguidance.append(conditioning=self.pos_cond, guidance=cfg_guid)[0]
            if neg is None:
                self._guider(model, cfg_guid)
            else:
                self._guider(model, cfg_guid, neg=True)
        else:
            if changed == cfg_guid and hasattr(self, "pos_cond"):
                if neg is None:
                    if "skip_emptyneg" in self.sca_dict["extra_opts"]:
                        self._guider(model, cfg_guid)
                elif hasattr(self, "neg_cond"):
                    self._guider(model, cfg_guid, neg=True)
            else:
                self.pos_cond = self.sdclip.encode(clip=clip, text=pos[0])[0]
                if neg is None:
                    if "skip_emptyneg" in self.sca_dict["extra_opts"]:
                        self._guider(model, cfg_guid)
                    else:
                        neg_copy = self.pos_cond.copy()
                        self.neg_cond = self.cond_zero_out.zero_out(conditioning=neg_copy)[0]
                        self._guider(model, cfg_guid, neg=True)
                elif neg is not None:
                    self.neg_cond = self.sdclip.encode(clip=clip, text=neg[0])[0]
                    self._guider(model, cfg_guid, neg=True)
                else:
                    logger.info("Error: get_guider()")

    def _get_sigmas(self, changed="ALL"):
        model, scheduler, denoise, steps = self._getitem(self._get_dicts["sigmas_dict"])
        if changed == "ALL":
            self.sigmas = self.basic_scheduler.get_sigmas(model=model, scheduler=scheduler, steps=steps, denoise=denoise)[0]

    def _get_sampler(self, changed="ALL"):
        sampler_name = self._getitem(self._get_dicts["sampler_dict"])
        if changed == "ALL":
            self.sampler = sampler_object(sampler_name)

    def _get_latent(self, changed="ALL"):
        width, height = self._getitem(self._get_dicts["latent_dict"])
        if changed == "ALL":
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

    def _update__get_dicts(self):
        _get_dicts = {
            "guider_dict": {
                "model": self.sca_dict["model"],
                "clip": self.sca_dict["clip"],
                "pos": self.sca_dict["pos"],
                "neg": self.sca_dict["neg"],
                "cfg_guid": self.sca_dict["cfg_guid"]
            },
            "sigmas_dict": {
                "model": self.sca_dict["model"],
                "scheduler": self.sca_dict["scheduler"],
                "denoise": self.sca_dict["denoise"],
                "steps": self.sca_dict["steps"]
            },
            "sampler_dict": {
                "sampler_name": self.sca_dict["sampler_name"]
            },
            "latent_dict": {
                "width": self.sca_dict["width"],
                "height": self.sca_dict["height"]
            }
        }
        return _get_dicts

    def _getitem(self, input_dict):
        if isinstance(input_dict, dict):
            return list(input_dict.keys())
        raise TypeError("Input must be a dictionary")
