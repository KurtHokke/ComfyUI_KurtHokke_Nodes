from .loggers import get_logger
import node_helpers
import comfy.sd
from comfy.samplers import CFGGuider
from comfy_extras.nodes_custom_sampler import Noise_RandomNoise
from comfy.comfy_types import IO, InputTypeDict


import torch

logger, decoDebug = get_logger("all")

@decoDebug
class SampleAssembler:
    def __init__(self, models):
        self.models = []
        self.def_conds = {
            "t5xxl": "",
            "clip_l": "",
            "guidance": 1.0,
            "flux_cond": None,
            "pos": "",
            "neg": "",
            "pos_cond": None,
            "neg_cond": None,
            "cfg": 8.0,
        }
        self.conds = self.def_conds.copy()
        self.guider = None
        self.latent_opts = []
        self.latent_ch = None
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"

        self.set_models(models)
        #self.extra_opts = None

    def reset_conds(self):
        self.conds = self.def_conds.copy()

    def set_models(self, models=None):
        if self.models != models:
            self.models = models
            self.latent_ch = self.models[2].latent_channels

    def get_latent_noise(self, latent_opts, noise_seed, batch_size=1, device=None):
        if device is not None:
            self.device = device
        self.latent_opts = latent_opts
        latent = torch.zeros([batch_size, self.latent_ch, self.latent_opts[1] // 8, self.latent_opts[0] // 8], device=self.device)
        noise = Noise_RandomNoise(noise_seed)
        return ({"samples":latent}, noise)

    def set_conds(self, cfg_guidance: float, pos_prompts: (str, list[str]) = None, neg_prompts: (str, list[str]) = None):
        clip = self.models[1]
        if self.latent_ch == 16:
            if self.conds["t5xxl"] == pos_prompts[0] and self.conds["clip_l"] == pos_prompts[1] and self.conds["guidance"] == cfg_guidance:
                self.get_guider(skip=True)
                return
            else:
                self.reset_conds()
            t5xxl = pos_prompts[0]
            if len(pos_prompts) > 1:
                clip_l = pos_prompts[1]
            else:
                clip_l = t5xxl
            tokens = clip.tokenize(clip_l)
            tokens["t5xxl"] = clip.tokenize(t5xxl)["t5xxl"]
            conditioning = clip.encode_from_tokens_scheduled(tokens, add_dict={"guidance": cfg_guidance})
            flux_cond = node_helpers.conditioning_set_values(conditioning, {"guidance": cfg_guidance})
            self.conds = {**self.conds, "flux_cond": flux_cond, "guidance": cfg_guidance, "t5xxl": t5xxl, "clip_l": clip_l}
            return self.conds
        else:
            if self.conds["cfg"] != cfg_guidance:
                self.conds = {**self.conds, "cfg": cfg_guidance}
            if self.conds["pos"] == pos_prompts and self.conds["neg"] == neg_prompts:
                self.get_guider(skip=True)
                return
            else:
                self.reset_conds()
            pos_text = self.conds["pos"][0]
            neg_text = self.conds["neg"][0]
            pos_tokens = clip.tokenize(pos_text)
            neg_tokens = clip.tokenize(neg_text)
            pos_cond = clip.encode_from_tokens_scheduled(pos_tokens)
            neg_cond = clip.encode_from_tokens_scheduled(neg_tokens)
            self.conds = {**self.conds, "pos_cond": pos_cond, "neg_cond": neg_cond, "cfg": cfg_guidance, "pos": pos_text, "neg": neg_text}
            return self.conds

    def _guider(self):
        if self.guider is None:
            self.guider = CFGGuider(self.models[0])

    def get_guider(self, skip=False):
        self._guider()
        if skip:
            return self.guider
        if "flux_cond" in self.conds:
            positive = self.conds["flux_cond"]
            self.guider.inner_set_conds({"positive": positive})
        elif "pos_cond" in self.conds and "neg_cond" in self.conds:
            positive = self.conds["pos_cond"]
            negative = self.conds["neg_cond"]
            cfg = self.conds["cfg"]
            self.guider.set_conds(positive, negative)
            self.guider.set_cfg(cfg)
        else:
            return f"INVALID!!!!!!!!!!!!!!!!!!!\n{self.conds}"
        return self.guider

    def get_sigmas(self, scheduler, steps, denoise):
        model = self.models[0]
        total_steps = steps
        if denoise < 1.0:
            if denoise <= 0.0:
                return (torch.FloatTensor([]),)
            total_steps = int(steps/denoise)

        sigmas = comfy.samplers.calculate_sigmas(model.get_model_object("model_sampling"), scheduler, total_steps).cpu()
        sigmas = sigmas[-(steps + 1):]
        return sigmas