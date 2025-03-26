from khn.utils import CATEGORY, any, logger, CLIP_DTYPES, prefix

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

class UNETLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": { "unet_name": (folder_paths.get_filename_list("diffusion_models"), ),
                              "weight_dtype": (["default", "fp8_e4m3fn", "fp8_e4m3fn_fast", "fp8_e5m2"],)
                             }}
    RETURN_TYPES = ("MODEL",)
    FUNCTION = "load_unet"

    CATEGORY = "advanced/loaders"

    def load_unet(self, unet_name, weight_dtype):
        model_options = {}
        if weight_dtype == "fp8_e4m3fn":
            model_options["dtype"] = torch.float8_e4m3fn
        elif weight_dtype == "fp8_e4m3fn_fast":
            model_options["dtype"] = torch.float8_e4m3fn
            model_options["fp8_optimizations"] = True
        elif weight_dtype == "fp8_e5m2":
            model_options["dtype"] = torch.float8_e5m2

        unet_path = folder_paths.get_full_path_or_raise("diffusion_models", unet_name)
        model = comfy.sd.load_diffusion_model(unet_path, model_options=model_options)
        return (model,)

class LoadUnetAndClip:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "unet_name": (folder_paths.get_filename_list("diffusion_models"),),
                "weight_dtype": (["default", "fp8_e4m3fn", "fp8_e4m3fn_fast", "fp8_e5m2"],),
                "clip_name1": (folder_paths.get_filename_list("text_encoders"), ),
                "clip_name2": (folder_paths.get_filename_list("text_encoders"), ),
                "type": (["flux", "sd3", "sdxl", "hunyuan_video"], ),
                "CLIPskip": ("INT", {"default": -1, "min": -24, "max": -1, "step": 1}),
                },
            "optional": {
                "device": (["default", "cpu"], {"advanced": True}),
            }
        }
    RETURN_TYPES = ("UnetClipPipe", )
    FUNCTION = "load_unet"

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.LOADERS.value

    def load_unet(self, unet_name, weight_dtype, clip_name1, clip_name2, type, CLIPskip, device="default",):
        model_options = {}
        if weight_dtype == "fp8_e4m3fn":
            model_options["dtype"] = torch.float8_e4m3fn
        elif weight_dtype == "fp8_e4m3fn_fast":
            model_options["dtype"] = torch.float8_e4m3fn
            model_options["fp8_optimizations"] = True
        elif weight_dtype == "fp8_e5m2":
            model_options["dtype"] = torch.float8_e5m2

        unet_path = folder_paths.get_full_path_or_raise("diffusion_models", unet_name)
        model = comfy.sd.load_diffusion_model(unet_path, model_options=model_options)

        clip_path1 = folder_paths.get_full_path_or_raise("text_encoders", clip_name1)
        clip_path2 = folder_paths.get_full_path_or_raise("text_encoders", clip_name2)
        clip_type = None

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
            "CLIP_dtype" : (CLIP_DTYPES, ),
            "CLIPskip": ("INT", {"default": -1, "min": -24, "max": -1, "step": 1}),
        }}

    RETURN_TYPES = ("UnetClipPipe", "MODEL", "CLIP", "VAE")
    FUNCTION = "load_ckpt"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.LOADERS.value

    def load_ckpt(self, ckpt_name, CLIP_dtype, CLIPskip):
        from comfy.sd import load_checkpoint_guess_config

        if CLIP_dtype == "fp16":
            te_model_options = {"dtype": torch.float16}
        elif CLIP_dtype == "fp32":
            te_model_options = {"dtype": torch.float32}
        elif CLIP_dtype == "fp8_e4m3fn":
            te_model_options = {"dtype": torch.float8_e4m3fn}
        elif CLIP_dtype == "fp8_e4m3fn_fast":
            te_model_options = {"dtype": torch.float8_e4m3fn, "fp8_optimizations": True}
        elif CLIP_dtype == "fp8_e5m2":
            te_model_options = {"dtype": torch.float8_e5m2}
        else:
            te_model_options = {}

        ckpt_path = folder_paths.get_full_path_or_raise("checkpoints", ckpt_name)
        out = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, embedding_directory=folder_paths.get_folder_paths("embeddings"), te_model_options=te_model_options)

        model = out[0]
        clip = out[1]
        vae = out[2]

        clip = clip.clone()
        clip.clip_layer(CLIPskip)

        UnetClipPipe = []

        UnetClipPipe.append(model)
        UnetClipPipe.append(clip)

        return (UnetClipPipe, model, clip, vae, )

class NoModel_CkptLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"), {"tooltip": "The name of the checkpoint (model) to load."}),
            }
        }
    RETURN_TYPES = ("CLIP", "VAE")
    FUNCTION = "load_nomodel_checkpoint"

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.LOADERS.value

    def load_nomodel_checkpoint(self, ckpt_name):
        ckpt_path = folder_paths.get_full_path_or_raise("checkpoints", ckpt_name)
        out = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, embedding_directory=folder_paths.get_folder_paths("embeddings"), output_model=False)
        clip = out[1]
        vae = out[2]
        return (clip, vae)

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
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

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
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

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

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.LORAS.value

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

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.LORAS.value

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


NODE_CLASS_MAPPINGS = {
    "LoadUnetAndClip": LoadUnetAndClip,
    "UnetClipLoraLoader": UnetClipLoraLoader,
    "UnetClipLoraLoaderBasic": UnetClipLoraLoaderBasic,
    "CkptPipe": CkptPipe,
    "NoModel_CkptLoader": NoModel_CkptLoader,
    "ModelPipe1": ModelPipe1,
    "ModelPipe2": ModelPipe2,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadUnetAndClip": prefix + "LoadUnetAndClip",
    "UnetClipLoraLoader": prefix + "UnetClipLoraLoader",
    "UnetClipLoraLoaderBasic": prefix + "UnetClipLoraLoaderBasic",
    "CkptPipe": prefix + "CkptPipe",
    "NoModel_CkptLoader": prefix + "NoModel_CkptLoader",
    "ModelPipe1": prefix + ">ModelPipe",
    "ModelPipe2": prefix + "<ModelPipe",
}