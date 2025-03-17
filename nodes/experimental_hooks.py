from __future__ import annotations
from typing import TYPE_CHECKING
from collections.abc import Iterable

if TYPE_CHECKING:
    from comfy.sd import CLIP
import comfy.sd
import comfy.utils
import comfy.hooks
from comfy_extras.nodes_hooks import CreateHookLora
import folder_paths
from ..utils import CATEGORY, NONE_EMBEDDINGS
from ..loggers import get_logger
from comfy.comfy_types import IO, ComfyNodeABC, InputTypeDict

logger, log_all = get_logger("log_all")

class CreateHookLoraTestSelf:
    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "lora_name": (folder_paths.get_filename_list("loras"), ),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01}),
                "strength_clip": ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01}),
            },
            "optional": {
                "prev_hooks": ("HOOKS",)
            }
        }

    EXPERIMENTAL = True
    RETURN_TYPES = ("HOOKS",)
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.HOOKS.value
    FUNCTION = "create_hook"

    def create_hook(self, lora_name: str, strength_model: float, strength_clip: float, prev_hooks: comfy.hooks.HookGroup=None):
        if prev_hooks is None:
            prev_hooks = comfy.hooks.HookGroup()
        prev_hooks.clone()

        if strength_model == 0 and strength_clip == 0:
            return (prev_hooks,)

        lora_path = folder_paths.get_full_path("loras", lora_name)
        lora = None
        if self.loaded_lora is not None:
            if self.loaded_lora[0] == lora_path:
                lora = self.loaded_lora[1]
            else:
                temp = self.loaded_lora
                self.loaded_lora = None
                del temp

        if lora is None:
            lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
            self.loaded_lora = (lora_path, lora)

        hooks = comfy.hooks.create_hook_lora(lora=lora, strength_model=strength_model, strength_clip=strength_clip)
        return (prev_hooks.clone_and_combine(hooks),)

@log_all
class expHook:
    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(s) -> InputTypeDict:
        return {"required": {
                    "lora_name": (folder_paths.get_filename_list("loras"), ),
                    "strength_model": ("FLOAT", {"default": 1.00, "min": -20.0, "max": 20.0, "step": 0.001}),
                    "strength_clip": ("FLOAT", {"default": 1.00, "min": -20.0, "max": 20.0, "step": 0.001}),
            },  "optional": {
                    "extra_opts": ("EXTRA_OPTS",),
                    "prev_hooks": ("HOOKS",),
                    "prev_hook_kf": ("HOOK_KEYFRAMES",),
            }
        }
    EXPERIMENTAL = True
    RETURN_TYPES = ("HOOKS", "HOOK_KEYFRAMES")
    FUNCTION = "create_hook"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.HOOKS.value
    DESCRIPTION = "Creates a hook for a given LoRA and sets the strength of the hook based on the strength of the LoRA."

    def create_hook(self, lora_name: str, strength_model: float, strength_clip: float, extra_opts: tuple=None,
                    prev_hooks: comfy.hooks.HookGroup=None,
                    prev_hook_kf: comfy.hooks.HookKeyframeGroup=None):
        if prev_hooks is None:
            prev_hooks = comfy.hooks.HookGroup()
        prev_hooks.clone()

        if strength_model == 0 and strength_clip == 0:
            return prev_hooks, prev_hook_kf

        lora_path = folder_paths.get_full_path("loras", lora_name)
        lora = None
        if self.loaded_lora is not None:
            if self.loaded_lora[0] == lora_path:
                lora = self.loaded_lora[1]
            else:
                temp = self.loaded_lora
                self.loaded_lora = None
                del temp
        if lora is None:
            lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
            self.loaded_lora = (lora_path, lora)
        hooks = comfy.hooks.create_hook_lora(lora=lora, strength_model=strength_model, strength_clip=strength_clip)


        if extra_opts is not None:
            strength_start = extra_opts[0]
            strength_end = extra_opts[1]
            interpolation = extra_opts[2]
            start_percent = extra_opts[3]
            end_percent = extra_opts[4]
            keyframes_count = extra_opts[5]
            print_keyframes = extra_opts[6]
            if prev_hook_kf is None:
                prev_hook_kf = comfy.hooks.HookKeyframeGroup()
            prev_hook_kf = prev_hook_kf.clone()
            percents = comfy.hooks.InterpolationMethod.get_weights(num_from=start_percent, num_to=end_percent, length=keyframes_count,
                                                                   method=comfy.hooks.InterpolationMethod.LINEAR)
            strengths = comfy.hooks.InterpolationMethod.get_weights(num_from=strength_start, num_to=strength_end, length=keyframes_count, method=interpolation)

            is_first = True
            for percent, strength in zip(percents, strengths):
                guarantee_steps = 0
                if is_first:
                    guarantee_steps = 1
                    is_first = False
                prev_hook_kf.add(comfy.hooks.HookKeyframe(strength=strength, start_percent=percent, guarantee_steps=guarantee_steps))
                if print_keyframes:
                    logger.info(f"Hook Keyframe - start_percent:{percent} = {strength}")

            if prev_hook_kf is not None:
                hooks = prev_hooks.clone_and_combine(hooks)
                hooks.set_keyframes_on_hooks(hook_kf=prev_hook_kf)
            return hooks, prev_hook_kf
        else:
            return prev_hooks, prev_hook_kf


class CreateHookWithKF:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "lora_name": (folder_paths.get_filename_list("loras"), ),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01}),
                "strength_clip": ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01}),
                "interpolation": (comfy.hooks.InterpolationMethod._LIST, ),
                "start_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001}),
                "end_percent": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001}),
                "strength_start": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.001}, ),
                "strength_end": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.001}, ),
            },
            "optional": {
                "prev_hooks": ("HOOKS",),
                "prev_hook_kf": ("HOOK_KEYFRAMES",),
                "extra_opts": ("EXTRA_OPTS",),
            }
        }
    RETURN_TYPES = ("HOOKS",)
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.HOOKS.value
    FUNCTION = "create_hook_with_kf"

    def create_hook_with_kf(self, lora_name: str, strength_model: float, strength_clip: float, interpolation: str,
                            start_percent: float, end_percent: float, strength_start: float, strength_end: float,
                            prev_hooks=None, prev_hook_kf=None, extra_opts=None):
        HookInstance = HookHandler()

        if extra_opts is None:
            extra_opts = {}

        if prev_hook_kf is not None:
            prev_hook_kf = HookInstance.create_hook_kf_interpolation(strength_start=strength_start, strength_end=strength_end, interpolation=interpolation,
                                start_percent=start_percent, end_percent=end_percent, keyframes_count=5, prev_hook_kf=prev_hook_kf)[0]
        else:
            prev_hook_kf = HookInstance.create_hook_kf_interpolation(strength_start=strength_start, strength_end=strength_end, interpolation=interpolation,
                                  start_percent=start_percent, end_percent=end_percent, keyframes_count=5)[0]
        if prev_hooks is not None:
            prev_hooks = HookInstance.create_hook(lora_name=lora_name, strength_model=strength_model, strength_clip=strength_clip, prev_hooks=prev_hooks)[0]
        else:
            prev_hooks = HookInstance.create_hook(lora_name=lora_name, strength_model=strength_model, strength_clip=strength_clip)[0]
        logger.info(f"prev_hooks: {type(prev_hooks)}")
        logger.info(f"prev_hook_kf: {type(prev_hook_kf)}")
        hooks = HookInstance.set_hook_keyframes(hooks=prev_hooks, hook_kf=prev_hook_kf)
        return (hooks,)

class SetModelHooksOnCond:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": ("CONDITIONING",),
                "hooks": ("HOOKS",),
            },
        }

    EXPERIMENTAL = True
    RETURN_TYPES = ("CONDITIONING",)
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.HOOKS.value
    FUNCTION = "attach_hook"

    def attach_hook(self, conditioning, hooks: comfy.hooks.HookGroup):
        return (comfy.hooks.set_hooks_for_conditioning(conditioning, hooks),)


class SetHookKeyframes:
    NodeId = 'SetHookKeyframes'
    NodeName = 'Set Hook Keyframes'
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "hooks": ("HOOKS",),
            },
            "optional": {
                "hook_kf": ("HOOK_KEYFRAMES",),
            }
        }

    EXPERIMENTAL = True
    RETURN_TYPES = ("HOOKS",)
    CATEGORY = "advanced/hooks/scheduling"
    FUNCTION = "set_hook_keyframes"

    def set_hook_keyframes(self, hooks: comfy.hooks.HookGroup, hook_kf: comfy.hooks.HookKeyframeGroup=None):
        if hook_kf is not None:
            hooks = hooks.clone()
            hooks.set_keyframes_on_hooks(hook_kf=hook_kf)
        return (hooks,)



'''
class AIO_Hooks:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "loras": ("LORA_NAMES", ),
                "apply_clip_hooks": ("BOOLEAN", {"default": True}),
                "apply_cond_hooks": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "clip": (IO.CLIP,),
                "prev_hooks": ("HOOKS",),
                "prev_hook_kf": ("HOOK_KEYFRAMES",),
                "extra_opts": ("EXTRA_OPTS",),
            }
        }
    RETURN_TYPES = ("HOOKS",)
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.HOOKS.value
    FUNCTION = "create_hook_with_kf"

    def create_hook_with_kf(self, loras: dict, clip=None, prev_hooks=None, prev_hook_kf=None, extra_opts=None):
        HookInstance = HookHandler()
        lora_starts = []
        lora_configs = []
        for i in range(1, 5):  # Processes "lora_1" to "lora_4"
            lora_name_key = f"lora_name_{i}"
            lora_settings_key = f"lora_settings_{i}"
            interpolation_key = f"interpolation_{i}"
            if lora_name_key in loras:
                lora_name = loras[lora_name_key]
                lora_settings = loras[lora_settings_key]
                interpolation = loras[interpolation_key]
                lora_strength, lora_start, lora_end = [float(value) for value in lora_settings.split(",")]
                lora_configs.append({
                    "name": lora_name,
                    "strength": lora_strength,
                    "start": lora_start,
                    "end": lora_end,
                    "interpolation": interpolation
                })
                lora_starts.append(lora_start)
        lora_configs.sort(key=lambda x: x["start"])

        for idx, lora_config in enumerate(lora_configs):
            if idx == 0:  # First Lora
                prev_hooks = HookInstance.create_hook_helper(HookInstance, lora_config, prev_hooks=prev_hooks)
                prev_hook_kf = HookInstance.create_hook_kf_helper(HookInstance, lora_config, prev_hook_kf=prev_hook_kf)

            else:  # Remaining Loras
                prev_hooks = HookInstance.create_hook_helper(HookInstance, lora_config, prev_hooks=prev_hooks)
                prev_hook_kf = HookInstance.create_hook_kf_helper(HookInstance, lora_config, prev_hook_kf=prev_hook_kf)

        return (hooks,)

'''