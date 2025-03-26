
#Stolen from https://github.com/mcmonkeyprojects/sd-dynamic-thresholding
#Thanks!

from ..utils import CATEGORY, prefix
#from custom_nodes.sd-dynamic-thresholding.dynthres_core import DynThresh
import importlib

# Import the module with a hyphen in its name
module_name = 'custom_nodes.sd-dynamic-thresholding.dynthres_core'
dyn_thresh_module = importlib.import_module(module_name)

# Now you can access DynThresh from the imported module
DynThresh = dyn_thresh_module.DynThresh


class DynamicThresholding:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "UnetClipPipe": ("UnetClipPipe",),
                "mimic_scale": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0, "step": 0.01}),
                "threshold_percentile": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "mimic_mode": (DynThresh.Modes, ),
                "mimic_scale_min": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 0.01}),
                "cfg_mode": (DynThresh.Modes, ),
                "cfg_scale_min": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 0.01}),
                "sched_val": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 100.0, "step": 0.01}),
                "separate_feature_channels": (["enable", "disable"], ),
                "scaling_startpoint": (DynThresh.Startpoints, ),
                "variability_measure": (DynThresh.Variabilities, ),
                "interpolate_phi": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                }
        }

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "patch"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.ADVANCED.value

    def patch(self, UnetClipPipe, mimic_scale, threshold_percentile, mimic_mode, mimic_scale_min, cfg_mode, cfg_scale_min, sched_val, separate_feature_channels, scaling_startpoint, variability_measure, interpolate_phi):

        model, clip = UnetClipPipe

        dynamic_thresh = DynThresh(mimic_scale, threshold_percentile, mimic_mode, mimic_scale_min, cfg_mode, cfg_scale_min, sched_val, 0, 999, separate_feature_channels == "enable", scaling_startpoint, variability_measure, interpolate_phi)
        
        def sampler_dyn_thresh(args):
            input = args["input"]
            cond = input - args["cond"]
            uncond = input - args["uncond"]
            cond_scale = args["cond_scale"]
            time_step = model.model.model_sampling.timestep(args["sigma"])
            time_step = time_step[0].item()
            dynamic_thresh.step = 999 - time_step

            if cond_scale == mimic_scale:
                return input - (uncond + (cond - uncond) * cond_scale)
            else:
                return input - dynamic_thresh.dynthresh(cond, uncond, cond_scale, None)

        m = model.clone()
        m.set_model_sampler_cfg_function(sampler_dyn_thresh)
        return (m, )

class DynamicThresholdingBasic:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "UnetClipPipe": ("UnetClipPipe",),
                "mimic_scale": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0, "step": 0.01}),
                "threshold_percentile": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                }
        }

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "patch"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.ADVANCED.value

    def patch(self, UnetClipPipe, mimic_scale, threshold_percentile):

        model, clip = UnetClipPipe

        dynamic_thresh = DynThresh(mimic_scale, threshold_percentile, "CONSTANT", 0, "CONSTANT", 0, 0, 0, 999, False, "MEAN", "AD", 1)
        
        def sampler_dyn_thresh(args):
            input = args["input"]
            cond = input - args["cond"]
            uncond = input - args["uncond"]
            cond_scale = args["cond_scale"]
            time_step = model.model.model_sampling.timestep(args["sigma"])
            time_step = time_step[0].item()
            dynamic_thresh.step = 999 - time_step

            if cond_scale == mimic_scale:
                return input - (uncond + (cond - uncond) * cond_scale)
            else:
                return input - dynamic_thresh.dynthresh(cond, uncond, cond_scale, None)

        m = model.clone()
        m.set_model_sampler_cfg_function(sampler_dyn_thresh)
        return (m, )
