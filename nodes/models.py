from .. import utils
from ..utils import CATEGORY, any

from typing import TYPE_CHECKING, Union
import logging
import torch
from collections.abc import Iterable

import torch
import comfy.hooks
from comfy.hooks import HookGroup, HookKeyframeGroup
from comfy_extras.nodes_hooks import CreateHookKeyframesInterpolated, CreateHookLora, SetHookKeyframes, SetClipHooks, CombineHooks
import comfy.sd
import comfy.utils
import folder_paths
if TYPE_CHECKING:
    from comfy.sd import CLIP

class LoadUnetAndClip:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "unet_name": (folder_paths.get_filename_list("diffusion_models"),),
                **utils.get_weight_dtype_inputs(),
                "clip_name1": (folder_paths.get_filename_list("text_encoders"), ),
                "clip_name2": (folder_paths.get_filename_list("text_encoders"), ),
                "type": (["sdxl", "sd3", "flux", "hunyuan_video"], ),
                "CLIPskip": ("INT", {"default": -1, "min": -24, "max": -1, "step": 1}),
                },
            "optional": {
                "device": (["default", "cpu"], {"advanced": True}),
            }
        }
    RETURN_TYPES = ("UnetClipPipe", )
    FUNCTION = "load_unet"

    CATEGORY = CATEGORY.MAIN.value + "/Loader"

    def load_unet(self, unet_name, weight_dtype, clip_name1, clip_name2, type, CLIPskip, device="default",):
        model_options = {}
        model_options = utils.parse_weight_dtype(model_options, weight_dtype)

        unet_path = folder_paths.get_full_path_or_raise("diffusion_models", unet_name)
        model = comfy.sd.load_diffusion_model(unet_path, model_options=model_options)

        clip_path1 = folder_paths.get_full_path_or_raise("text_encoders", clip_name1)
        clip_path2 = folder_paths.get_full_path_or_raise("text_encoders", clip_name2)
        if type == "sdxl":
            clip_type = comfy.sd.CLIPType.STABLE_DIFFUSION
        elif type == "sd3":
            clip_type = comfy.sd.CLIPType.SD3
        elif type == "flux":
            clip_type = comfy.sd.CLIPType.FLUX
        elif type == "hunyuan_video":
            clip_type = comfy.sd.CLIPType.HUNYUAN_VIDEO

        model_options = {}
        if device == "cpu":
            model_options["load_device"] = model_options["offload_device"] = torch.device("cpu")

        clip = comfy.sd.load_clip(ckpt_paths=[clip_path1, clip_path2], embedding_directory=folder_paths.get_folder_paths("embeddings"), clip_type=clip_type, model_options=model_options)
        clip = clip.clone()
        clip.clip_layer(CLIPskip)

        UnetClipPipe = []

        UnetClipPipe.append(model)
        UnetClipPipe.append(clip)

        return (UnetClipPipe, )


class CkptPipe:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "ckpt_name": (folder_paths.get_filename_list("checkpoints"), {"tooltip": "The name of the checkpoint (model) to load."}),
            "CLIPskip": ("INT", {"default": -1, "min": -24, "max": -1, "step": 1}),
        }}

    RETURN_TYPES = ("UnetClipPipe", "VAE")
    FUNCTION = "load_ckpt"
    CATEGORY = CATEGORY.MAIN.value + "/Loader"

    def load_ckpt(self, ckpt_name, CLIPskip):
        from nodes import CheckpointLoaderSimple
        model, clip, vae = CheckpointLoaderSimple.load_checkpoint(self, ckpt_name)

        clip = clip.clone()
        clip.clip_layer(CLIPskip)

        UnetClipPipe = []

        UnetClipPipe.append(model)
        UnetClipPipe.append(clip)

        return (UnetClipPipe, vae, )


class ModelPipe1:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "MODEL": ("MODEL", ),
                "CLIP": ("CLIP", ),
            }
        }

    RETURN_TYPES = ("UnetClipPipe", )
    FUNCTION = "do_pipe"
    CATEGORY = CATEGORY.MAIN.value + "/Utils"

    def do_pipe(self, MODEL, CLIP):
        model = MODEL
        clip = CLIP

        UnetClipPipe = []
        UnetClipPipe.append(model)
        UnetClipPipe.append(clip)
        return (UnetClipPipe, )


class ModelPipe2:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "UnetClipPipe": ("UnetClipPipe", ),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP")
    FUNCTION = "un_pipe"
    CATEGORY = CATEGORY.MAIN.value + "/Utils"

    def un_pipe(self, UnetClipPipe):
        model, clip = UnetClipPipe
        return (model, clip, )


class UnetClipLoraLoader:
    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "UnetClipPipe": ("UnetClipPipe", ),
                "lora_name": (folder_paths.get_filename_list("loras"), {"tooltip": "The name of the LoRA."}),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.001, "tooltip": "How strongly to modify the diffusion model. This value can be negative."}),
                "strength_clip": ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.001, "tooltip": "How strongly to modify the CLIP model. This value can be negative."}),
            }
        }

    RETURN_TYPES = ("UnetClipPipe",)
    FUNCTION = "load_lora"

    CATEGORY = CATEGORY.MAIN.value + "/Loras"

    def load_lora(self, lora_name, strength_model, strength_clip, UnetClipPipe=None):
        if strength_model == 0 and strength_clip == 0:
            return (UnetClipPipe,)

        lora_path = folder_paths.get_full_path_or_raise("loras", lora_name)
        lora = None
        if self.loaded_lora is not None:
            if self.loaded_lora[0] == lora_path:
                lora = self.loaded_lora[1]
            else:
                self.loaded_lora = None

        if lora is None:
            lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
            self.loaded_lora = (lora_path, lora)

        model, clip = UnetClipPipe

        model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, strength_model, strength_clip)

        UnetClipPipe = []
        UnetClipPipe.append(model_lora)
        UnetClipPipe.append(clip_lora)

        return (UnetClipPipe, )



class UnetClipLoraLoaderBasic:
    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "UnetClipPipe": ("UnetClipPipe", ),
                "lora_name": (folder_paths.get_filename_list("loras"), {"tooltip": "The name of the LoRA."}),
                "strength": ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.001, "tooltip": "How strongly to modify the diffusion model. This value can be negative."}),
            }
        }

    RETURN_TYPES = ("UnetClipPipe", )
    FUNCTION = "load_lora"

    CATEGORY = CATEGORY.MAIN.value + "/Loras"

    def load_lora(self, lora_name, strength, UnetClipPipe=None):

        if strength == 0:
            return (UnetClipPipe,)

        lora_path = folder_paths.get_full_path_or_raise("loras", lora_name)
        lora = None
        if self.loaded_lora is not None:
            if self.loaded_lora[0] == lora_path:
                lora = self.loaded_lora[1]
            else:
                self.loaded_lora = None

        if lora is None:
            lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
            self.loaded_lora = (lora_path, lora)

        strength_model = strength
        strength_clip = strength
        
        model, clip = UnetClipPipe

        model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, strength_model, strength_clip)

        UnetClipPipe = []
        UnetClipPipe.append(model_lora)
        UnetClipPipe.append(clip_lora)

        return (UnetClipPipe, )

