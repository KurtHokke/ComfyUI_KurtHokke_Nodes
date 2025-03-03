from ..names import CATEGORY
from .. import utils
import torch
from ..utils import any

import comfy.sd
import comfy.utils
import folder_paths

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

class UnetClipLoraLoader:
    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "UnetClipPipe": (any, ),
                "lora_name": (folder_paths.get_filename_list("loras"), {"tooltip": "The name of the LoRA."}),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01, "tooltip": "How strongly to modify the diffusion model. This value can be negative."}),
                "strength_clip": ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01, "tooltip": "How strongly to modify the CLIP model. This value can be negative."}),
            }
        }

    RETURN_TYPES = ("UnetClipPipe", "MODEL", "CLIP")
    FUNCTION = "load_lora"

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.LOADERS.value
    DESCRIPTION = "LoRAs are used to modify diffusion and CLIP models, altering the way in which latents are denoised such as applying styles. Multiple LoRA nodes can be linked together."

    def load_lora(self, lora_name, strength_model, strength_clip, UnetClipPipe=None):
        model, clip = UnetClipPipe
        if strength_model == 0 and strength_clip == 0:
            return (UnetClipPipe, model, clip)

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

        model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, strength_model, strength_clip)

        UnetClipPipe = []
        UnetClipPipe.append(model_lora)
        UnetClipPipe.append(clip_lora)
        return (UnetClipPipe, model_lora, clip_lora)

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