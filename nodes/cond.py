from ..utils import CATEGORY
from comfy.comfy_types import IO, ComfyNodeABC, InputTypeDict
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

class ConditioningProcessor:

    def addWeighted(self, conditioning_to, conditioning_from, conditioning_to_strength):
        out = []
        if len(conditioning_from) > 1:
            logging.warning("Warning: ConditioningAverage conditioning_from contains more than 1 cond, only the first one will actually be applied to conditioning_to.")
        cond_from = conditioning_from[0][0]
        pooled_output_from = conditioning_from[0][1].get("pooled_output", None)

        for i in range(len(conditioning_to)):
            t1 = conditioning_to[i][0]
            pooled_output_to = conditioning_to[i][1].get("pooled_output", pooled_output_from)
            t0 = cond_from[:,:t1.shape[1]]
            if t0.shape[1] < t1.shape[1]:
                t0 = torch.cat([t0] + [torch.zeros((1, (t1.shape[1] - t0.shape[1]), t1.shape[2]))], dim=1)

            tw = torch.mul(t1, conditioning_to_strength) + torch.mul(t0, (1.0 - conditioning_to_strength))
            t_to = conditioning_to[i][1].copy()
            if pooled_output_from is not None and pooled_output_to is not None:
                t_to["pooled_output"] = torch.mul(pooled_output_to, conditioning_to_strength) + torch.mul(pooled_output_from, (1.0 - conditioning_to_strength))
            elif pooled_output_from is not None:
                t_to["pooled_output"] = pooled_output_from

            n = [tw, t_to]
            out.append(n)
        return (out, )


    def concat(self, conditioning_to, conditioning_from):
        out = []
        print(conditioning_from)
        print(conditioning_to)
        if len(conditioning_from) > 1:
            logging.warning("Warning: ConditioningConcat conditioning_from contains more than 1 cond, only the first one will actually be applied to conditioning_to.")

        cond_from = conditioning_from[0][0]
        print(cond_from)
        for i in range(len(conditioning_to)):
            t1 = conditioning_to[i][0]
            print(t1)
            tw = torch.cat((t1, cond_from),1)
            print(tw)
            n = [tw, conditioning_to[i][1].copy()]
            print(n)
            out.append(n)
            print(out)
        return (out, )

    def combine(self, conditioning_1, conditioning_2):
        return (conditioning_1 + conditioning_2, )

    '''
    def combine(self, conditioning):
        if len(conditioning) > 1:
            combined = conditioning[0]

            for item in conditioning[1:]:
                # Depending on your requirements, you can define the combination logic
                combined += item

            return (combined,)
    '''


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
            prev_cond = []
        else:
            prev_cond = prev_cond.copy()
        prev_cond.append(cond)
        return (clip, prev_cond, )


