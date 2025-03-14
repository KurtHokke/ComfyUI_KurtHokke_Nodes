from ..utils import CATEGORY, logger
from comfy.comfy_types import IO, ComfyNodeABC, InputTypeDict
import random
import torch
import logging

class mycombine:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "inputcount": ("INT", {"default": 2, "min": 2, "max": 20, "step": 1}),
                "operation": (["combine", "concat"], {"default": "combine"}),
                "conditioning_1": ("CONDITIONING", ),
                "conditioning_2": ("CONDITIONING", ),
            },
    }

    RETURN_TYPES = ("CONDITIONING", "INT")
    RETURN_NAMES = ("combined", "inputcount")
    FUNCTION = "combine"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.CONDITIONING.value
    DESCRIPTION = """
Combines multiple conditioning nodes into one
"""

    def combine(self, inputcount, operation, **kwargs):
        from nodes import ConditioningCombine
        from nodes import ConditioningConcat
        cond_combine_node = ConditioningCombine()
        cond_concat_node = ConditioningConcat()
        cond = kwargs["conditioning_1"]
        for c in range(1, inputcount):
            new_cond = kwargs[f"conditioning_{c + 1}"]
            if operation == "combine":
                cond = cond_combine_node.combine(new_cond, cond)[0]
            elif operation == "concat":
                cond = cond_concat_node.concat(cond, new_cond)[0]
        return (cond, inputcount,)


class splitcond:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": ("CONDITIONING", ),
            },
        }
    RETURN_TYPES = ("CONDITIONING", "CONDITIONING")
    RETURN_NAMES = ("cond1", "cond2")
    FUNCTION = "split"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.CONDITIONING.value

    def split(self, conditioning):
        cond1 = [conditioning[0]]
        cond2 = conditioning[1]
        return (cond1, cond2)


class ApplyCondsExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": ("CONDITIONING", ),
                "extra_opts": ("EXTRA_OPTS", ),
            },
        }
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "apply_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.CONDITIONING.value

    def apply_extra_opts(self, conditioning, extra_opts):
        if len(conditioning) != 2:
            return conditioning
        else:
            if extra_opts is not None and "cond" in extra_opts:
                if "cond_direction1" in extra_opts and extra_opts["cond_direction1"] == '<':
                    conditioning1 = [conditioning[0]]
                    conditioning2 = conditioning[1]
                    logger.info(f"<: {conditioning1}\n{conditioning2}")
                elif "cond_direction1" in extra_opts and extra_opts["cond_direction1"] == '>':
                    conditioning1 = conditioning[1]
                    conditioning2 = [conditioning[0]]
                    logger.info(f">: {conditioning1}\n{conditioning2}")
                else:
                    conditioning1 = [conditioning[0]]
                    conditioning2 = conditioning[1]
                    logger.info(f"<>: {conditioning1}\n{conditioning2}")

                if "WAS_blend1" in extra_opts:
                    from custom_nodes.was_extras.ConditioningBlend import WAS_ConditioningBlend
                    get_blend = WAS_ConditioningBlend()
                    if "WAS_blend_mode1" in extra_opts and "strength1" in extra_opts:
                        blend_mode = extra_opts["WAS_blend_mode1"]
                        strength = extra_opts["strength1"]
                        logger.info(f"blend_mode: {blend_mode}\nblend_strength: {strength}")
                    else:
                        logger.info(f"WAS_blend_mode not found in\n{extra_opts}")
                        return conditioning

                    if "seed1" in extra_opts:
                        seed = extra_opts["seed1"]
                        logger.info(f"seed: {seed}")
                    else:
                        seed = random.randint(0, 0xffffffffffffffff)
                        logger.info(f"seed not in extra opts, generating random seed:\n{seed}")
                    conditioning_WAS_blend = get_blend.combine(conditioning1, conditioning2, blend_mode, strength, seed=int(seed))[0]
                    conditioning = [conditioning_WAS_blend,]

                if "combine1" in extra_opts:
                    from nodes import ConditioningCombine
                    cond_combine = ConditioningCombine()
                    conditioning_combined = cond_combine.combine(conditioning1, conditioning2)[0]
                    conditioning = [conditioning_combined,]

                elif "concat1" in extra_opts:
                    from nodes import ConditioningConcat
                    cond_concat = ConditioningConcat()
                    conditioning_concatenated = cond_concat.concat(conditioning1, conditioning2)[0]
                    conditioning = [conditioning_concatenated,]

                elif "average1" in extra_opts:
                    from nodes import ConditioningAverage
                    cond_average = ConditioningAverage()
                    strength = extra_opts["strength1"]
                    conditioning_averaged = cond_average.addWeighted(conditioning1, conditioning2, strength)[0]
                    conditioning = [conditioning_averaged,]

                return conditioning
            else:
                print(f"extra_opts: {extra_opts} is not a valid input for this node.")
                return conditioning


class ChainTextEncode(ComfyNodeABC):
    @classmethod
    def INPUT_TYPES(s) -> InputTypeDict:
        return {
            "required": {
                "text": (IO.STRING, {"multiline": True, "dynamicPrompts": True, "tooltip": "The text to be encoded."}),
                "clip": (IO.CLIP, {"tooltip": "The CLIP model used for encoding the text."})
            },
            "optional": {
                "prev_cond": ("CONDITIONING",)
            }
        }
    RETURN_TYPES = ("CLIP", "CONDITIONING",)
    FUNCTION = "encode_append"

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.CONDITIONING.value
    DESCRIPTION = "Encodes a text prompt using a CLIP model into an embedding that can be used to guide the diffusion model towards generating specific images."

    def encode_append(self, clip, text, prev_cond=None):
        if clip is None:
            raise RuntimeError("ERROR: clip input is invalid: None\n\nIf the clip is from a checkpoint loader node your checkpoint does not contain a valid clip or text encoder model.")
        tokens = clip.tokenize(text)
        cond = clip.encode_from_tokens_scheduled(tokens)
        if prev_cond is None:
            prev_cond = cond
        else:
            prev_cond = prev_cond.copy()
            prev_cond.append(cond)
        return (clip, prev_cond, )


