from ..utils import CATEGORY, COND_OPTS, COND_DIRECTION, NONE_LORAS, any
from ..loggers import get_logger
from nodes import MAX_RESOLUTION
from custom_nodes.was_extras.ConditioningBlend import blending_modes
from comfy.comfy_types import *
import folder_paths
import comfy.hooks

logger, log_all = get_logger("log_all")

class ViewExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "extra_opts": ("EXTRA_OPTS", ),
                }
        }
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("string", )
    FUNCTION = "view_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.EXTRAOPTS.value

    def view_extra_opts(self, extra_opts):
        if not isinstance(extra_opts, dict):
            return "Invalid input. Expected a dictionary."

        # Build the string
        string = ""
        for key, value in extra_opts.items():
            string += f"{key}: {value}\n"
            logger.debug(f"string: {string}")

        return (string, )

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

class KeyframeExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "strength_start": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.001}, ),
                "strength_end": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.001}, ),
                "interpolation": (["linear", "ease_in", "ease_out", "ease_in_out"], ),
                "start_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001}),
                "end_percent": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001}),
                "keyframes_count": ("INT", {"default": 5, "min": 2, "max": 100, "step": 1}),
                "print_keyframes": ("BOOLEAN", {"default": False}),
            }
        }
    RETURN_TYPES = ("EXTRA_OPTS", )
    RETURN_NAMES = ("extra_opts", )
    FUNCTION = "pack_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.EXTRAOPTS.value

    def pack_extra_opts(self, strength_start, strength_end, interpolation, start_percent, end_percent, keyframes_count, print_keyframes):
        extra_opts = []
        extra_opts.append(strength_start)
        extra_opts.append(strength_end)
        extra_opts.append(interpolation)
        extra_opts.append(start_percent)
        extra_opts.append(end_percent)
        extra_opts.append(keyframes_count)
        extra_opts.append(print_keyframes)
        return (extra_opts, )

class LoraSettingsExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                "interpolation_1": (comfy.hooks.InterpolationMethod._LIST, ),
                "interpolation_2": (comfy.hooks.InterpolationMethod._LIST, ),
                "interpolation_3": (comfy.hooks.InterpolationMethod._LIST, ),
                "interpolation_4": (comfy.hooks.InterpolationMethod._LIST, ),
                }
        }
    RETURN_TYPES = ("LORA_SETTINGS", )
    RETURN_NAMES = ("lora_settings", )
    FUNCTION = "pack_lora_settings"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.HOOKS.value

    def pack_lora_settings(self, interpolation_1, interpolation_2, interpolation_3, interpolation_4):
        lora_settings = {}
        if interpolation_1 != "None":
            lora_settings = {**lora_settings, "interpolation_1": interpolation_1}
        if interpolation_2 != "None":
            lora_settings = {**lora_settings, "interpolation_2": interpolation_2}
        if interpolation_3 != "None":
            lora_settings = {**lora_settings, "interpolation_3": interpolation_3}
        if interpolation_4 != "None":
            lora_settings = {**lora_settings, "interpolation_4": interpolation_4}
        return (lora_settings, )

class LoraNamesExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "lora_name_1": (NONE_LORAS, ),
                    "lora_settings_1": ("STRING", {"default": "1.0,0.0,0.25", "tooltip": "float(strength)','float(start)','float(end)"}),
                    "lora_name_2": (NONE_LORAS, ),
                    "lora_settings_2": ("STRING", {"default": "1.0,0.25,0.5", "tooltip": "float(strength)','float(start)','float(end)"}),
                    "lora_name_3": (NONE_LORAS, ),
                    "lora_settings_3": ("STRING", {"default": "1.0,0.5,0.75", "tooltip": "float(strength)','float(start)','float(end)"}),
                    "lora_name_4": (NONE_LORAS, ),
                    "lora_settings_4": ("STRING", {"default": "1.0,0.75,1.0", "tooltip": "float(strength)','float(start)','float(end)"}),
                },
                "optional": {
                    "lora_settings": ("LORA_SETTINGS", ),
                }
        }
    RETURN_TYPES = ("LORA_NAMES", )
    RETURN_NAMES = ("lora_names", )
    FUNCTION = "pack_lora_names"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.HOOKS.value

    def pack_lora_names(self, lora_name_1, lora_settings_1, lora_name_2, lora_settings_2,
                        lora_name_3, lora_settings_3, lora_name_4, lora_settings_4, lora_settings=None):
        if lora_settings is None:
            lora_settings = {}
        loranames = {}
        if lora_name_1 != "None":
            loranames = {**loranames, "lora_name_1": lora_name_1, "lora_settings_1": lora_settings_1}
            if "interpolation_1" in lora_settings:
                lora_settings = {**lora_settings, "interpolation_1": lora_settings["interpolation_1"]}
            else:
                lora_settings = {**lora_settings, "interpolation_1": "linear"}
        if lora_name_2 != "None":
            loranames = {**loranames, "lora_name_2": lora_name_2, "lora_settings_2": lora_settings_2}
            if "interpolation_2" in lora_settings:
                lora_settings = {**lora_settings, "interpolation_2": lora_settings["interpolation_2"]}
            else:
                lora_settings = {**lora_settings, "interpolation_2": "linear"}
        if lora_name_3 != "None":
            loranames = {**loranames, "lora_name_3": lora_name_3, "lora_settings_3": lora_settings_3}
            if "interpolation_3" in lora_settings:
                lora_settings = {**lora_settings, "interpolation_3": lora_settings["interpolation_3"]}
            else:
                lora_settings = {**lora_settings, "interpolation_3": "linear"}
        if lora_name_4 != "None":
            loranames = {**loranames, "lora_name_4": lora_name_4, "lora_settings_4": lora_settings_4}
            if "interpolation_4" in lora_settings:
                lora_settings = {**lora_settings, "interpolation_4": lora_settings["interpolation_4"]}
            else:
                lora_settings = {**lora_settings, "interpolation_4": "linear"}
        loranames = {**lora_settings, **loranames}
        return (loranames, )


class MultiplyTensorsExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "enable_cond_1": ("BOOLEAN", {"default": False, "label_on": "On", "label_off": "Off"}),
                    "factor_1": ("FLOAT", {"default": 1.000, "min": -100.000, "max": 100.000, "step": 0.001}),
                    "factor_pooled_1": ("FLOAT", {"default": 1.000, "min": -100.000, "max": 100.000, "step": 0.001}),
                    "enable_cond_2": ("BOOLEAN", {"default": False, "label_on": "On", "label_off": "Off"}),
                    "factor_2": ("FLOAT", {"default": 1.000, "min": -100.000, "max": 100.000, "step": 0.001}),
                    "factor_pooled_2": ("FLOAT", {"default": 1.000, "min": -100.000, "max": 100.000, "step": 0.001}),
                },
                "optional": {
                    "prev_opts": ("EXTRA_OPTS", ),
                }
        }
    RETURN_TYPES = ("EXTRA_OPTS", )
    RETURN_NAMES = ("extra_opts", )
    FUNCTION = "pack_extra_opts"

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.EXTRAOPTS.value

    def pack_extra_opts(self, enable_cond_1, factor_1, factor_pooled_1, enable_cond_2, factor_2, factor_pooled_2, prev_opts=None):
        extra_opts = {}
        if prev_opts is None:
            prev_opts = {}
        if enable_cond_1 is True:
            extra_opts1 = {"cond_multiply_factor_1": factor_1}
            extra_opts2 = {"cond_multiply_factor_pooled_1": factor_pooled_1}
            extra_opts = {**extra_opts1, **extra_opts2}
        if enable_cond_2 is True:
            extra_opts1 = {"cond_multiply_factor_2": factor_2}
            extra_opts2 = {"cond_multiply_factor_pooled_2": factor_pooled_2}
            extra_opts = {**extra_opts, **extra_opts1, **extra_opts2}
        if extra_opts != {}:
            cond_extra_opts = {"cond": True, "cond_multiply": True}
            extra_opts = {**prev_opts, **cond_extra_opts, **extra_opts}
        return (extra_opts, )

class TensorsExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "which_cond": ("INT", {"default": 1, "min": 1, "max": 10}),
            "norm_tensor": ("BOOLEAN", {"default": False, "label_on": "On", "label_off": "Off"}),
            "standardize_tensor": ("BOOLEAN", {"default": False, "label_on": "On", "label_off": "Off"}),
            "pool_mean": ("BOOLEAN", {"default": False, "label_on": "On", "label_off": "Off"}),
            #"pool_std": ("BOOLEAN", {"default": False, "label_on": "On", "label_off": "Off"}),
            #"pool_min": ("BOOLEAN", {"default": False, "label_on": "On", "label_off": "Off"}),
            "pool_max": ("BOOLEAN", {"default": False, "label_on": "On", "label_off": "Off"}),
            "pool_sequence": ("BOOLEAN", {"default": False, "label_on": "On", "label_off": "Off"}),
            "clamp_tensor": ("BOOLEAN", {"default": False, "label_on": "On", "label_off": "Off"}),
            "squeeze_tensor": ("BOOLEAN", {"default": False, "label_on": "On", "label_off": "Off"}),
            },
            "optional": {
                "prev_opts": ("EXTRA_OPTS", ),
            }
        }
    RETURN_TYPES = ("EXTRA_OPTS", )
    RETURN_NAMES = ("extra_opts", )
    FUNCTION = "pack_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.EXTRAOPTS.value

    def pack_extra_opts(self, which_cond, norm_tensor, standardize_tensor, pool_mean, pool_max, pool_sequence, clamp_tensor, squeeze_tensor, prev_opts=None):
        extra_opts = {}
        if prev_opts is None:
            prev_opts = {}
        if norm_tensor is True:
            extra_opts = {**extra_opts, "norm_tensor": "norm_tensor"}
        if standardize_tensor is True:
            extra_opts = {**extra_opts, "standardize_tensor": "standardize_tensor"}
        if pool_mean is True:
            extra_opts = {**extra_opts, "pool_mean": "pool_mean"}
        if pool_max is True:
            extra_opts = {**extra_opts, "pool_max": "pool_max"}
        if pool_sequence is True:
            extra_opts = {**extra_opts, "pool_sequence": "pool_sequence"}
        if clamp_tensor is True:
            extra_opts = {**extra_opts, "clamp_tensor": "clamp_tensor"}
        if squeeze_tensor is True:
            extra_opts = {**extra_opts, "squeeze_tensor": "squeeze_tensor"}

        if extra_opts != {}:

            extra_opts = {**prev_opts, "cond_tensors": True, "which_cond_tensors": which_cond, **extra_opts, }
        return (extra_opts, )

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

class COND_SET_STRENGTH_ExtraOpts:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "enable_cond_1": ("BOOLEAN", {"default": True, "label_on": "On", "label_off": "Off"}),
                    "enable_cond_2": ("BOOLEAN", {"default": True, "label_on": "On", "label_off": "Off"}),
                    "strength_1": ("FLOAT", {"default": 1.000, "min": -100.000, "max": 100.000, "step": 0.001}),
                    "strength_2": ("FLOAT", {"default": 1.000, "min": -100.000, "max": 100.000, "step": 0.001}),
                },
                "optional": {
                    "prev_opts": ("EXTRA_OPTS", ),
                }
        }
    RETURN_TYPES = ("EXTRA_OPTS", )
    RETURN_NAMES = ("extra_opts", )
    FUNCTION = "pack_extra_opts"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.EXTRAOPTS.value

    def pack_extra_opts(self, enable_cond_1, enable_cond_2, strength_1, strength_2, prev_opts=None):
        extra_opts = {}
        if prev_opts is None:
            prev_opts = {}
        if enable_cond_1 is True:
            extra_opts1 = {"cond_set_strength_1": strength_1}
            extra_opts = {**extra_opts1}
        if enable_cond_2 is True:
            extra_opts2 = {"cond_set_strength_2": strength_2}
            extra_opts = {**extra_opts, **extra_opts2}
        if extra_opts != {}:
            cond_extra_opts = {"cond": True, "cond_set_strength": True}
            extra_opts = {**cond_extra_opts, **extra_opts}

        get_merged_opts = MergeExtraOpts()
        extra_opts = get_merged_opts.merge_extra_opts(prev_opts, extra_opts)
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
        if enabled is True:
            cond_extra_opts = {"cond": True}
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
            elif operation == "combine":
                extra_opts1 = {"combine": True}
                extra_opts = {**extra_opts1}

            elif operation == "concat":
                extra_opts1 = {"concat": True}
                extra_opts2 = {"cond_direction": direction}
                extra_opts = {**extra_opts1, **extra_opts2}

            elif operation == "average":
                extra_opts1 = {"average": True}
                extra_opts2 = {"cond_direction": direction}
                extra_opts3 = {"strength": strength}
                extra_opts = {**extra_opts1, **extra_opts2, **extra_opts3}
            else:
                extra_opts = {}
        else:
            cond_extra_opts = {}
            extra_opts = {}

        extra_opts = {**cond_extra_opts, **extra_opts}


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
            cond_extra_opts = {"cond": True}
            extra_opts1 = {"schedule_cfg": schedule}
            extra_opts2 = {"from_cfg": from_cfg}
            extra_opts3 = {"to_cfg": to_cfg}
            extra_opts = {**cond_extra_opts, **extra_opts1, **extra_opts2, **extra_opts3}
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