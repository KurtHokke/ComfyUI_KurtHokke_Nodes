from ..names import CATEGORY
from .. import utils
from ..utils import any

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
    RETURN_TYPES = ("UnetClipPipe",)
    FUNCTION = "load_unet"

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.LOADERS.value

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

        return (UnetClipPipe,)


class CkptPipe:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "ckpt_name": (folder_paths.get_filename_list("checkpoints"), {"tooltip": "The name of the checkpoint (model) to load."}),
            "CLIPskip": ("INT", {"default": -1, "min": -24, "max": -1, "step": 1}),
        }}

    RETURN_TYPES = ("UnetClipPipe", "VAE")
    FUNCTION = "load_ckpt"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.LOADERS.value

    def load_ckpt(self, ckpt_name, CLIPskip):
        from nodes import CheckpointLoaderSimple
        model, clip, vae = CheckpointLoaderSimple.load_checkpoint(self, ckpt_name)

        clip = clip.clone()
        clip.clip_layer(CLIPskip)

        UnetClipPipe = []

        UnetClipPipe.append(model)
        UnetClipPipe.append(clip)

        return (UnetClipPipe, vae,)


class ModelPipe1:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "MODEL": ("MODEL", ),
                "CLIP": ("CLIP", ),
            }
        }

    RETURN_TYPES = ("UnetClipPipe",)
    FUNCTION = "do_pipe"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.PATCH.value

    def do_pipe(self, MODEL, CLIP):
        model = MODEL
        clip = CLIP

        UnetClipPipe = []
        UnetClipPipe.append(model)
        UnetClipPipe.append(clip)
        return (UnetClipPipe,)


class ModelPipe2:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "UnetClipPipe": (any, ),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP")
    FUNCTION = "un_pipe"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.PATCH.value

    def un_pipe(self, UnetClipPipe):
        model, clip = UnetClipPipe
        return (model, clip)


class UnetClipLoraLoader:
    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "UnetClipPipe": (any, ),
                "lora_name": (folder_paths.get_filename_list("loras"), {"tooltip": "The name of the LoRA."}),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.001, "tooltip": "How strongly to modify the diffusion model. This value can be negative."}),
                "strength_clip": ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.001, "tooltip": "How strongly to modify the CLIP model. This value can be negative."}),
            }
        }

    RETURN_TYPES = ("UnetClipPipe",)
    FUNCTION = "load_lora"

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.PATCH.value

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

        return (UnetClipPipe)



class UnetClipLoraLoaderBasic:
    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "UnetClipPipe": (any, ),
                "lora_name": (folder_paths.get_filename_list("loras"), {"tooltip": "The name of the LoRA."}),
                "strength": ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.001, "tooltip": "How strongly to modify the diffusion model. This value can be negative."}),
            }
        }

    RETURN_TYPES = ("UnetClipPipe",)
    FUNCTION = "load_lora"

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.PATCH.value

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

        return (UnetClipPipe,)

'''
class LoraHookSchedulerBasic:
    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "UnetClipPipe": (any, ),
                "lora_name": (folder_paths.get_filename_list("loras"), {"tooltip": "The name of the LoRA."}),
                "lora_strength": ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.001, "tooltip": "How strongly to modify the diffusion model. This value can be negative."}),
                "strength_start": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.001}, ),
                "strength_end": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.001}, ),
                "interpolation": (comfy.hooks.InterpolationMethod._LIST, ),
                "start_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001}),
                "end_percent": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001}),
                "keyframes_count": ("INT", {"default": 5, "min": 2, "max": 100, "step": 1}),
            }
        }

    EXPERIMENTAL = True
    RETURN_TYPES = ("UnetClipPipe",)
    FUNCTION = "load_hooklora"

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.PATCH.value

    #model, clip, prev_hooks, prev_hook_kf = UnetClipPipe

    def load_hooklora(self, lora_name: str, lora_strength: float, strength_start: float, strength_end: float, interpolation: str,
                      start_percent: float, end_percent: float, keyframes_count: int, UnetClipPipe=None):

        if len(UnetClipPipe) == 2:
            model, clip = UnetClipPipe
            prev_hooks = None  # Default value if not provided
            prev_hook_kf = None  # Default value if not provided
        elif len(UnetClipPipe) == 4:
            model, clip, prev_hooks, prev_hook_kf = UnetClipPipe
            prev_hook_kf = prev_hook_kf[0]
            prev_hooks = prev_hooks[0]
        else:
            raise ValueError(f"Unexpected number of elements in UnetClipPipe: {len(UnetClipPipe)}")

        hooks_a = prev_hooks

        strength_model = lora_strength
        strength_clip = lora_strength
        print_keyframes = False

        
        hook_keyframes_creator = CreateHookKeyframesInterpolated()
        hook_kf_tuple = hook_keyframes_creator.create_hook_keyframes(strength_start=strength_start, strength_end=strength_end, interpolation=interpolation,
                                                                      start_percent=start_percent, end_percent=end_percent, keyframes_count=keyframes_count,
                                                                      print_keyframes=print_keyframes, prev_hook_kf=prev_hook_kf)
        hook_kf = hook_kf_tuple[0]

        
        hooks_lora_creator = CreateHookLora()
        hooks_tuple = hooks_lora_creator.create_hook(lora_name=lora_name, strength_model=strength_model, strength_clip=strength_clip)
        
        hooks = hooks_tuple[0]

        apply_scheduling = SetHookKeyframes()
        scheduled_hooks_tuple = apply_scheduling.set_hook_keyframes(hooks=hooks, hook_kf=hook_kf)

        scheduled_hooks = scheduled_hooks_tuple[0]


        if hooks_a is not None:
            hooks_b = scheduled_hooks
            merge_hooks = CombineHooks()
            final_hooks = merge_hooks.combine_hooks(hooks_A=hooks_a, hooks_B=hooks_b)
        else:
            final_hooks = scheduled_hooks


        UnetClipPipe = []
        UnetClipPipe.append(model)
        UnetClipPipe.append(clip)
        UnetClipPipe.append(final_hooks)
        UnetClipPipe.append(hook_kf)

        return (UnetClipPipe,)


class ModelPipeHooks:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "UnetClipPipe": (any, ),
                "apply_to_conds": ("BOOLEAN", {"default": True}),
                "schedule_clip": ("BOOLEAN", {"default": False})
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP")
    FUNCTION = "un_pipe_apply_hooks"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.PATCH.value

    def un_pipe_apply_hooks(self, UnetClipPipe, schedule_clip: bool, apply_to_conds: bool):
        
        if len(UnetClipPipe) == 2:
            model, clip = UnetClipPipe
            final_hooks = None  # Default value if not provided
            hook_kf = None  # Default value if not provided
        elif len(UnetClipPipe) == 4:
            model, clip, final_hooks, hook_kf = UnetClipPipe
            print(final_hooks)
            lenhooks = final_hooks[0]
            print(len(lenhooks))
        else:
            raise ValueError(f"Unexpected number of elements in UnetClipPipe: {len(UnetClipPipe)}")

        hooks = final_hooks

        grouphook = HookGroup()
        apply_all_hooks = SetClipHooks()
        clip_w_hooks = apply_all_hooks.apply_hooks(clip=clip, schedule_clip=schedule_clip, apply_to_conds=apply_to_conds)
        print(clip_w_hooks)

        return (model, clip_w_hooks)


'''
'''
class LoraLoader:
    def __init__(self):
        self.loaded_lora_01 = None
        self.loaded_lora_02 = None
        self.loaded_lora_03 = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "UnetClipPipe": (any, ),

                "lora_name_01": (['None'] + folder_paths.get_filename_list("loras"), ),
                "strength_model_01":("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01}),
                "strength_clip_01":("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01}),

                "lora_name_02": (['None'] + folder_paths.get_filename_list("loras"), ),
                "strength_model_02":("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01}),
                "strength_clip_02":("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01}),

                "lora_name_03": (['None'] + folder_paths.get_filename_list("loras"), ),
                "strength_model_03":("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01}),
                "strength_clip_03":("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("UnetClipPipe", "MODEL", "CLIP")
    FUNCTION = "load_lora"

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.LOADERS.value

    def load_lora(self, UnetClipPipe=None, lora_name_01, strength_model_01, strength_clip_01, lora_name_02, strength_model_02, strength_clip_02, lora_name_03, strength_model_03, strength_clip_03):
        model, clip = UnetClipPipe
        if strength_model_01 == 0 and strength_clip_01 == 0 and strength_model_02 == 0 and strength_clip_02 == 0 and strength_model_03 == 0 and strength_clip_03 == 0:
            return (UnetClipPipe, model, clip)

        if lora_name_01 != None:
            lora_path_01 = folder_paths.get_full_path_or_raise("loras", lora_name_01)
            lora_01 = None
            if self.loaded_lora_01 is not None:
                if self.loaded_lora_01[0] == lora_path_01:
                    lora_01 = self.loaded_lora_01[1]
                else:
                    self.loaded_lora_01 = None

        if lora_name_02 != None:
            lora_path_02 = folder_paths.get_full_path_or_raise("loras", lora_name_02)
            lora_02 = None
            if self.loaded_lora_02 is not None:
                if self.loaded_lora_02[0] == lora_path_02:
                    lora_02 = self.loaded_lora_02[1]
                else:
                    self.loaded_lora_02 = None

        if lora_name_03 != None:
            lora_path_03 = folder_paths.get_full_path_or_raise("loras", lora_name_03)
            lora_03 = None
            if self.loaded_lora_03 is not None:
                if self.loaded_lora_03[0] == lora_path_03:
                    lora_03 = self.loaded_lora_03[1]
                else:
                    self.loaded_lora_03 = None

        if lora_01 is None:
            lora_01 = comfy.utils.load_torch_file(lora_path_01, safe_load=True)
            self.loaded_lora_01 = (lora_path_01, lora_01)
        if lora_02 is None:
            lora_02 = comfy.utils.load_torch_file(lora_path_02, safe_load=True)
            self.loaded_lora_02 = (lora_path_02, lora_02)
        if lora_03 is None:
            lora_03 = comfy.utils.load_torch_file(lora_path_03, safe_load=True)
            self.loaded_lora_03 = (lora_path_03, lora_03)

        if self.loaded_lora_01 is not None:
            model_lora_01, clip_lora_01 = comfy.sd.load_lora_for_models(model, clip, lora_01, strength_model_01, strength_clip_01)
        if self.loaded_lora_02 is not None:
            model_lora_01, clip_lora_01 = comfy.sd.load_lora_for_models(model, clip, lora_01, strength_model_01, strength_clip_01)
        else:
            UnetClipPipe.append(model)
            UnetClipPipe.append(clip)
        if self.loaded_lora_03 is not None:
            model_lora_01, clip_lora_01 = comfy.sd.load_lora_for_models(model, clip, lora_01, strength_model_01, strength_clip_01)
        return (model_lora, clip_lora)

'''