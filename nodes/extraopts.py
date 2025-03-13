from ..utils import CATEGORY, COND_OPTS, COND_DIRECTION

class MergeExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "extra_opts1": ("EXTRA_OPTS", ),
            },
            "optional": {
                "extra_opts2": ("EXTRA_OPTS", ),
            }
        }
    RETURN_TYPES = ("EXTRA_OPTS", )
    RETURN_NAMES = ("extra_opts", )
    FUNCTION = "merge_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.EXTRAOPTS.value

    def merge_extra_opts(self, extra_opts1=None, extra_opts2=None):
        if extra_opts1 is None:
            extra_opts1 = {}
        if extra_opts2 is None:
            extra_opts2 = {}
        extra_opts2_with_suffix = {f"{key}1": value for key, value in extra_opts2.items()}

        extra_opts = {**extra_opts1, **extra_opts2_with_suffix}
        return (extra_opts, )


class COND_ExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "affected_conds": ("STRING", {"default": "1,2", "multiline": False}),
                    "operation": (COND_OPTS, ),
                    "direction": (COND_DIRECTION, ),
                    "average_strength": ("FLOAT", {"default": 0.500, "min": 0.000, "max": 1.000, "step": 0.001}),
                },
                "optional": {
                    "prev_opts": ("EXTRA_OPTS", ),
                }
        }
    RETURN_TYPES = ("EXTRA_OPTS", )
    RETURN_NAMES = ("extra_opts", )
    FUNCTION = "pack_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.EXTRAOPTS.value

    def pack_extra_opts(self, affected_conds, operation, direction, average_strength, prev_opts=None):
        def replace_suffix(key, suffix="2"):
            """Helper function to replace any suffix from the key with the new suffix"""
            if key[-1].isdigit():
                return f"{key[:-1]}{suffix}"
            else:
                return f"{key}{suffix}"

        if affected_conds != "":
            extra_opts1 = {"affected_conds": affected_conds}
            if operation == "combine":
                extra_opts2 = {"combine": True}
                extra_opts = {**extra_opts1, **extra_opts2}
                extra_opts_with_suffix = {f"{key}1": value for key, value in extra_opts.items()}
            elif operation == "concat":
                extra_opts2 = {"concat": True}
                extra_opts3 = {"cond_direction": direction}
                extra_opts = {**extra_opts1, **extra_opts2, **extra_opts3}
                extra_opts_with_suffix = {f"{key}1": value for key, value in extra_opts.items()}
            elif operation == "average":
                extra_opts2 = {"average": True}
                extra_opts3 = {"cond_direction": direction}
                extra_opts4 = {"average_strength": average_strength}
                extra_opts = {**extra_opts1, **extra_opts2, **extra_opts3, **extra_opts4}
                extra_opts_with_suffix = {f"{key}1": value for key, value in extra_opts.items()}
            else:
                extra_opts_with_suffix = {}
        else:
            extra_opts_with_suffix = {}

        if prev_opts is not None:
            extra_opts_with_suffix = {replace_suffix(key, "2"): value for key, value in extra_opts.items()}
            extra_opts = {**prev_opts, **extra_opts_with_suffix}
        else:
            extra_opts = extra_opts_with_suffix

        return (extra_opts, )


class VAE_ExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"switch": ("BOOLEAN", {"default": True, "label_on": "On", "label_off": "Off"}),
                             "tile_size": ("INT", {"default": 512, "min": 64, "max": 4096, "step": 32}),
                             "overlap": ("INT", {"default": 64, "min": 0, "max": 4096, "step": 32}),
                             "temporal_size": ("INT", {"default": 64, "min": 8, "max": 4096, "step": 4, "tooltip": "Only used for video VAEs: Amount of frames to decode at a time."}),
                             "temporal_overlap": ("INT", {"default": 8, "min": 4, "max": 4096, "step": 4, "tooltip": "Only used for video VAEs: Amount of frames to overlap."}),
                            }}
    RETURN_TYPES = ("EXTRA_OPTS", )
    RETURN_NAMES = ("extra_opts", )
    FUNCTION = "pack_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.EXTRAOPTS.value

    def pack_extra_opts(self, switch, tile_size, overlap, temporal_size, temporal_overlap):
        if switch:
            extra_opts = {"tile_size": tile_size, "overlap": overlap, "temporal_size": temporal_size, "temporal_overlap": temporal_overlap}
        else:
            extra_opts = {}
        return (extra_opts, )