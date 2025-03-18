from .loggers import get_logger
import node_helpers
import comfy.sd


import torch

logger, decoDebug = get_logger("all")

@decoDebug
class SampleAssembler:
    def __init__(self, models):
        self.models = []
        self.prompts = {
            "pos": [],
            "neg": [],
        }
        self.latent_opts = []
        self.latent_ch = None
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"

        self.set_models(models)
        #self.extra_opts = None

    def set_models(self, models=None):
        if self.models != models:
            self.models = models
            self.latent_ch = self.models[2].latent_channels

    def set_prompts(self, pos_prompts=None, neg_prompts=None):
        if self.prompts["pos"] != pos_prompts:
            self.prompts["pos"] = pos_prompts
        if self.prompts["neg"] != neg_prompts:
            self.prompts["neg"] = neg_prompts

    def setget_latent(self, latent_opts, batch_size=1, device=None):
        if device is not None:
            self.device = device
        self.latent_opts = latent_opts
        latent = torch.zeros([batch_size, self.latent_ch, self.latent_opts[1] // 8, self.latent_opts[0] // 8], device=self.device)
        return ({"samples":latent}, )

    def get_conds(self, cfg_guidance: float):
        clip = self.models[1]
        if self.latent_ch == 16:
            t5xxl = self.prompts["pos"][0]
            clip_l = self.prompts["pos"][1]
            return ({"t5xxl": t5xxl, "clip_l": clip_l}, )
            tokens = clip.tokenize(clip_l)
            tokens["t5xxl"] = clip.tokenize(t5xxl)["t5xxl"]

            return (clip.encode_from_tokens_scheduled(tokens, add_dict={"guidance": guidance}), )

            # = node_helpers.conditioning_set_values(conditioning, {"guidance": guidance})
