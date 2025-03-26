from __future__ import annotations
from typing import TYPE_CHECKING, Union
from collections.abc import Iterable
if TYPE_CHECKING:
    from comfy.sd import CLIP
import comfy.sd
import comfy.utils
import comfy.hooks
import folder_paths
from khn.utils import logger, CATEGORY
import torch

class HookHandler:
    def __init__(self):
        self.loaded_lora = None

    def create_hook_helper(self, instance, config, prev_hooks=None):
        return instance.create_hook(
            lora_name=config["name"],
            strength_model=config["strength"],
            strength_clip=config["strength"],
            prev_hooks=prev_hooks
        )[0]

    def create_hook_kf_helper(self, instance, config, prev_hook_kf=None, keyframes_count=5):
        return instance.create_hook_kf_interpolation(
            strength_start=1.0,
            strength_end=1.0,
            interpolation=config["interpolation"],
            start_percent=config["start"],
            end_percent=config["end"],
            keyframes_count=keyframes_count,
            prev_hook_kf=prev_hook_kf
        )[0]


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
                logger.debug(f"{lora} loaded")
            else:
                temp = self.loaded_lora
                self.loaded_lora = None
                del temp

        if lora is None:
            lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
            logger.debug(f"loaded {lora}")
            self.loaded_lora = (lora_path, lora)

        hooks = comfy.hooks.create_hook_lora(lora=lora, strength_model=strength_model, strength_clip=strength_clip)
        return (prev_hooks.clone_and_combine(hooks),)

    def create_hook_model_only(self, lora_name: str, strength_model: float, prev_hooks: comfy.hooks.HookGroup=None):
        return self.create_hook(lora_name=lora_name, strength_model=strength_model, strength_clip=0, prev_hooks=prev_hooks)

    def set_hook_keyframes(self, hooks: comfy.hooks.HookGroup, hook_kf: comfy.hooks.HookKeyframeGroup=None):
        if hook_kf is not None:
            hooks = hooks.clone()
            hooks.set_keyframes_on_hooks(hook_kf=hook_kf)
        return (hooks,)

    def create_hook_kf_basic(self, strength_mult: float, start_percent: float, prev_hook_kf: comfy.hooks.HookKeyframeGroup=None):
        if prev_hook_kf is None:
            prev_hook_kf = comfy.hooks.HookKeyframeGroup()
        prev_hook_kf = prev_hook_kf.clone()
        keyframe = comfy.hooks.HookKeyframe(strength=strength_mult, start_percent=start_percent)
        prev_hook_kf.add(keyframe)
        return (prev_hook_kf,)

    def create_hook_kf_interpolation(self, strength_start: float, strength_end: float, interpolation: str,
                              start_percent: float, end_percent: float, keyframes_count: int,
                              print_keyframes=False, prev_hook_kf: comfy.hooks.HookKeyframeGroup=None):
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
                logger.debug(f"Hook Keyframe - start_percent:{percent} = {strength}")
        return (prev_hook_kf,)

    def create_hook_kf_floats(self, floats_strength: Union[float, list[float]],
                              start_percent: float, end_percent: float,
                              prev_hook_kf: comfy.hooks.HookKeyframeGroup=None, print_keyframes=False):
        if prev_hook_kf is None:
            prev_hook_kf = comfy.hooks.HookKeyframeGroup()
        prev_hook_kf = prev_hook_kf.clone()
        if type(floats_strength) in (float, int):
            floats_strength = [float(floats_strength)]
        elif isinstance(floats_strength, Iterable):
            pass
        else:
            raise Exception(f"floats_strength must be either an iterable input or a float, but was{type(floats_strength).__repr__}.")
        percents = comfy.hooks.InterpolationMethod.get_weights(num_from=start_percent, num_to=end_percent, length=len(floats_strength),
                                                               method=comfy.hooks.InterpolationMethod.LINEAR)

        is_first = True
        for percent, strength in zip(percents, floats_strength):
            guarantee_steps = 0
            if is_first:
                guarantee_steps = 1
                is_first = False
            prev_hook_kf.add(comfy.hooks.HookKeyframe(strength=strength, start_percent=percent, guarantee_steps=guarantee_steps))
            if print_keyframes:
                logger.debug(f"Hook Keyframe - start_percent:{percent} = {strength}")
        return (prev_hook_kf,)

    def apply_clip_hooks(self, clip: CLIP, schedule_clip: bool, apply_to_conds: bool, hooks: comfy.hooks.HookGroup=None):
        if hooks is not None:
            clip = clip.clone()
            if apply_to_conds:
                clip.apply_hooks_to_conds = hooks
            clip.patcher.forced_hooks = hooks.clone()
            clip.use_clip_schedule = schedule_clip
            if not clip.use_clip_schedule:
                clip.patcher.forced_hooks.set_keyframes_on_hooks(None)
            clip.patcher.register_all_hook_patches(hooks, comfy.hooks.create_target_dict(comfy.hooks.EnumWeightTarget.Clip))
        return (clip,)

    def attach_hook(self, conditioning, hooks: comfy.hooks.HookGroup):
        return (comfy.hooks.set_hooks_for_conditioning(conditioning, hooks),)

    def create_cond_range(self, start_percent: float, end_percent: float):
        return ((start_percent, end_percent), (0.0, start_percent), (end_percent, 1.0))
    
    def set_properties(self, cond_NEW,
                       strength: float, set_cond_area: str,
                       mask: torch.Tensor=None, hooks: comfy.hooks.HookGroup=None, timesteps: tuple=None):
        (final_cond,) = comfy.hooks.set_conds_props(conds=[cond_NEW],
                                                   strength=strength, set_cond_area=set_cond_area,
                                                   mask=mask, hooks=hooks, timesteps_range=timesteps)
        return (final_cond,)
    
    def set_combine_properties(self, cond, cond_NEW,
                       strength: float, set_cond_area: str,
                       mask: torch.Tensor=None, hooks: comfy.hooks.HookGroup=None, timesteps: tuple=None):
        (final_cond,) = comfy.hooks.set_conds_props_and_combine(conds=[cond], new_conds=[cond_NEW],
                                                               strength=strength, set_cond_area=set_cond_area,
                                                               mask=mask, hooks=hooks, timesteps_range=timesteps)
        return (final_cond,)
    
    def set_pair_properties(self, positive_NEW, negative_NEW,
                       strength: float, set_cond_area: str,
                       mask: torch.Tensor=None, hooks: comfy.hooks.HookGroup=None, timesteps: tuple=None):
        final_positive, final_negative = comfy.hooks.set_conds_props(conds=[positive_NEW, negative_NEW],
                                                                    strength=strength, set_cond_area=set_cond_area,
                                                                    mask=mask, hooks=hooks, timesteps_range=timesteps)
        return (final_positive, final_negative)

    def set_pair_combine_properties(self, positive, negative, positive_NEW, negative_NEW,
                       strength: float, set_cond_area: str,
                       mask: torch.Tensor=None, hooks: comfy.hooks.HookGroup=None, timesteps: tuple=None):
        final_positive, final_negative = comfy.hooks.set_conds_props_and_combine(conds=[positive, negative], new_conds=[positive_NEW, negative_NEW],
                                                                                strength=strength, set_cond_area=set_cond_area,
                                                                                mask=mask, hooks=hooks, timesteps_range=timesteps)
        return (final_positive, final_negative)

    def combine_pair(self, positive_A, negative_A, positive_B, negative_B):
        final_positive, final_negative = comfy.hooks.set_conds_props_and_combine(conds=[positive_A, negative_A], new_conds=[positive_B, negative_B],)
        return (final_positive, final_negative,)

    def set_pair_default_and_combine(self, positive, negative, positive_DEFAULT, negative_DEFAULT,
                                hooks: comfy.hooks.HookGroup=None):
        final_positive, final_negative = comfy.hooks.set_default_conds_and_combine(conds=[positive, negative], new_conds=[positive_DEFAULT, negative_DEFAULT],
                                                                                   hooks=hooks)
        return (final_positive, final_negative)

    def set_default_and_combine(self, cond, cond_DEFAULT,
                                hooks: comfy.hooks.HookGroup=None):
        (final_conditioning,) = comfy.hooks.set_default_conds_and_combine(conds=[cond], new_conds=[cond_DEFAULT],
                                                                        hooks=hooks)
        return (final_conditioning,)