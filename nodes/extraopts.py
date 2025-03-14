from ..utils import CATEGORY, COND_OPTS, COND_DIRECTION, any
from nodes import MAX_RESOLUTION
from custom_nodes.was_extras.ConditioningBlend import blending_modes

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

        extra_opts = {**extra_opts1, **extra_opts2}
        return extra_opts

class NoNegExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "modify_pos_cfg": ("BOOLEAN", {"default": True, "label_on": "On", "label_off": "Off"} ),
                    "cfg": ("FLOAT", {"default": 0.000, "min": -100.000, "max": 1000.000, "step": 0.001}),
                },
                "optional": {
                    "prev_opts": ("EXTRA_OPTS", ),
                }
        }
    RETURN_TYPES = ("EXTRA_OPTS", )
    RETURN_NAMES = ("extra_opts", )
    FUNCTION = "pack_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.EXTRAOPTS.value

    def pack_extra_opts(self, modify_pos_cfg, cfg, prev_opts=None):
        if modify_pos_cfg is True and cfg > 0:
            extra_opts1 = {"modify_pos_cfg": cfg}
            extra_opts = {f"{key}1": value for key, value in extra_opts1.items()}
        else:
            extra_opts = {}
        if prev_opts is None:
            prev_opts = {}
        get_merged_opts = MergeExtraOpts()
        extra_opts = get_merged_opts.merge_extra_opts(prev_opts, extra_opts)

        return (extra_opts, )


class SEED_ExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                }
        }
    RETURN_TYPES = ("EXTRA_OPTS", )
    RETURN_NAMES = ("extra_opts", )
    FUNCTION = "pack_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.EXTRAOPTS.value

    def pack_extra_opts(self, seed):
        extra_opts = {"seed": seed}
        return (extra_opts, )

class COND_ExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "enabled": ("BOOLEAN", {"default": True, "label_on": "On", "label_off": "Off"}),
                    "operation": (COND_OPTS, ),
                    "WAS_blend_mode": (list(blending_modes.keys()), ),
                    "direction": (COND_DIRECTION, ),
                    "strength": ("FLOAT", {"default": 0.500, "min": -10.000, "max": 10.000, "step": 0.001}),
                },
                "optional": {
                    "prev_opts": ("EXTRA_OPTS", ),
                }
        }
    RETURN_TYPES = ("EXTRA_OPTS",)
    RETURN_NAMES = ("extra_opts",)
    FUNCTION = "pack_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.EXTRAOPTS.value

    def pack_extra_opts(self, enabled, operation, WAS_blend_mode, direction, strength, prev_opts=None):
        def replace_suffix(key, suffix="2"):
            if key[-1].isdigit():
                return f"{key[:-1]}{suffix}"
            else:
                return f"{key}{suffix}"
        extra_opts1 = ""
        extra_opts2 = ""
        extra_opts3 = ""
        extra_opts4 = ""
        extra_opts5 = ""
        if enabled is True:
            if operation == "WAS_blend":
                extra_opts1 = {"WAS_blend": True}
                extra_opts2 = {"WAS_blend_mode": WAS_blend_mode}
                extra_opts3 = {"cond_direction": direction}
                extra_opts4 = {"strength": strength}
                if prev_opts is not None:
                    if "seed" in prev_opts:
                        extra_opts5 = {"seed": prev_opts["seed"]}
                    else:
                        extra_opts5 = {}
                else:
                    extra_opts5 = {}
                    prev_opts = {}

                extra_opts = {**extra_opts1, **extra_opts2, **extra_opts3, **extra_opts4, **extra_opts5}
                extra_opts_with_suffix = {f"{key}1": value for key, value in extra_opts.items()}
            elif operation == "combine":
                extra_opts1 = {"combine": True}
                extra_opts = {**extra_opts1}
                extra_opts_with_suffix = {f"{key}1": value for key, value in extra_opts.items()}

            elif operation == "concat":
                extra_opts1 = {"concat": True}
                extra_opts2 = {"cond_direction": direction}
                extra_opts = {**extra_opts1, **extra_opts2}
                extra_opts_with_suffix = {f"{key}1": value for key, value in extra_opts.items()}

            elif operation == "average":
                extra_opts1 = {"average": True}
                extra_opts2 = {"cond_direction": direction}
                extra_opts3 = {"strength": strength}
                extra_opts = {**extra_opts1, **extra_opts2, **extra_opts3}
                extra_opts_with_suffix = {f"{key}1": value for key, value in extra_opts.items()}
            else:
                extra_opts_with_suffix = {}
        else:
            extra_opts = {"disabled": enabled}
            extra_opts_with_suffix = {f"{key}1": value for key, value in extra_opts.items()}

        cond_extra_opts = {"cond": True}
        extra_opts_with_suffix = {**cond_extra_opts, **extra_opts_with_suffix}

        extra_opts = extra_opts_with_suffix

        get_merged_opts = MergeExtraOpts()
        extra_opts = get_merged_opts.merge_extra_opts(prev_opts, extra_opts)

        return (extra_opts,)

class COND_ExtraOpts_2:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "enabled": ("BOOLEAN", {"default": True, "label_on": "On", "label_off": "Off"}),
                    "from_cfg": ("FLOAT", {"default": 6.5, "min": 0.0, "max": 100.0, "step": 0.1, "round": 0.01}),
                    "to_cfg": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 100.0, "step": 0.1, "round": 0.01}),
                    "schedule": (["linear", "log", "exp", "cos"], {'default': 'log'})
                },
                "optional": {
                    "prev_opts": ("EXTRA_OPTS", ),
                }
        }
    RETURN_TYPES = ("EXTRA_OPTS", )
    RETURN_NAMES = ("extra_opts", )
    FUNCTION = "pack_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.EXTRAOPTS.value

    def pack_extra_opts(self, enabled, from_cfg, to_cfg, schedule, prev_opts=None):
        if enabled is True:
            extra_opts1 = {"schedule_cfg": schedule}
            extra_opts2 = {"from_cfg": from_cfg}
            extra_opts3 = {"to_cfg": to_cfg}
            extra_opts = {**extra_opts1, **extra_opts2, **extra_opts3}
            extra_opts = {f"{key}1": value for key, value in extra_opts.items()}
        else:
            extra_opts = {}

        if prev_opts is None:
            prev_opts = {}

        get_merged_opts = MergeExtraOpts()
        extra_opts = get_merged_opts.merge_extra_opts(prev_opts, extra_opts)

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


class batchsize_ExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "batchsize": ("INT", {"default": 1, "min": 1, "max": 1000000, "step": 1}),
                    "dim_override": ("BOOLEAN", {"default": True, "label_on": "On", "label_off": "Off"}),
                    "width": ("INT", {"default": 1024, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
                    "height": ("INT", {"default": 1024, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
                }
        }
    RETURN_TYPES = ("EXTRA_OPTS", )
    RETURN_NAMES = ("extra_opts", )
    FUNCTION = "pack_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.EXTRAOPTS.value

    def pack_extra_opts(self, batchsize, dim_override, width, height):
        extra_opts1 = {"batchsize": batchsize}
        if dim_override and width > 0 and height > 0:
            extra_opts2 = {"width": width, "height": height}
            extra_opts = {**extra_opts1, **extra_opts2}
        else:
            extra_opts = extra_opts1

        return (extra_opts, )