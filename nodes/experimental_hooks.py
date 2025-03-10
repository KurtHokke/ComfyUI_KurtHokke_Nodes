from ..utils import CATEGORY
from comfy_extras.nodes_hooks import CreateHookLora, CreateHookKeyframe, SetHookKeyframes
from comfy.hooks import HookGroup
import folder_paths
from typing import TYPE_CHECKING, Union
import logging
import torch
from collections.abc import Iterable
if TYPE_CHECKING:
    from comfy.sd import CLIP
import comfy.hooks
import comfy.sd
import comfy.utils


class LoraHookChain:
    def __init__(self):
        self.CreateHookLora_instance = CreateHookLora()
        self.CreateHookKeyframe_instance = CreateHookKeyframe()
        self.SetHookKeyframes_instance = SetHookKeyframes()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "UnetClipPipe": ("UnetClipPipe", ),
                "lora_name": (folder_paths.get_filename_list("loras"), ),
                "strength": ("FLOAT", {"default": 0.75, "min": -20.0, "max": 20.0, "step": 0.01}),
                "strength_mult": ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01}),
                "start_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001}),
            }
        }

    EXPERIMENTAL = True
    RETURN_TYPES = ("UnetClipPipe",)
    CATEGORY = CATEGORY.MAIN.value + "/Advanced/Hooks"
    FUNCTION = "call_CreateHookLora"


    def call_CreateHookLora(self, UnetClipPipe, lora_name: str, strength: float, strength_mult: float, start_percent: float):
        if len(UnetClipPipe) == 2:
            model, clip = UnetClipPipe
            prev_hooks = None
            prev_hook_kf = None
        else:
            model, clip, prev_hooks, prev_hook_kf = UnetClipPipe
            prev_hooks = None
            prev_hook_kf = None

        strength_model = strength
        strength_clip = strength

        hook_group = HookGroup()
        len_before = hook_group.__len__()

        hook = self.CreateHookLora_instance.create_hook(lora_name, strength_model, strength_clip, prev_hooks)
        hook_kf = self.CreateHookKeyframe_instance.create_hook_keyframe(strength_mult, start_percent, prev_hook_kf)[0]
        if hook_kf is not None:
            hooks = hook_group.clone()
            hook_group.set_keyframes_on_hooks(hook_kf=hook_kf)

        len_after = hook_group.__len__()
        print(f"BEFORE ADDING HOOKS ------------------>>>>>> {len_before}")
        print(f"BEFORE ADDING HOOKS ------------------>>>>>> {len_before}")
        print(f"BEFORE ADDING HOOKS ------------------>>>>>> {len_before}")
        print(f"AFTER ADDING HOOKS ------------------>>>>>> {len_after}")
        print(f"AFTER ADDING HOOKS ------------------>>>>>> {len_after}")
        print(f"AFTER ADDING HOOKS ------------------>>>>>> {len_after}")

        UnetClipPipe = []
        UnetClipPipe.append(model)
        UnetClipPipe.append(clip)
        UnetClipPipe.append(hooks)
        UnetClipPipe.append(hook_kf)

        return(UnetClipPipe, )


class ModelPipe3:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "UnetClipPipe": ("UnetClipPipe", ),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP", "HOOKS", "HOOK_KEYFRAMES")
    RETURN_NAMES = ("MODEL", "CLIP", "HOOKS", "HOOK_KF")
    FUNCTION = "un_pipe"
    CATEGORY = CATEGORY.MAIN.value + "/Advanced/Hooks"

    def un_pipe(self, UnetClipPipe):
        if len(UnetClipPipe) == 2:
            model, clip = UnetClipPipe
            return (model, clip, )
        else:
            model, clip, hooks, hook_kf = UnetClipPipe
            return (model, clip, hooks, hook_kf, )