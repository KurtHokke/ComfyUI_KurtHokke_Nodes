'''
    !DISCLAIMER! I'm very new to programming and I've been heavily inspired by following.
https://github.com/crystian/ComfyUI-Crystools
https://github.com/cubiq/ComfyUI_essentials
  Many thanks goes to these awesome developers!
'''
from .nodes.util_nodes import Node_BOOL, Node_INT, Node_Float, Node_String, Node_StringMultiline
from .nodes.pipe import BooleanToPipe, BooleanFromPipe
from .nodes.math import ExpMath, ExpMathDual, ExpMathQuad
from .nodes.misc import EmptyLatentSize, EmptyLatentSize64, SchedulerSel, SamplerSel, LoraFluxParams
from .nodes.models import LoadUnetAndClip, UnetClipLoraLoader, UnetClipLoraLoaderBasic, CkptPipe, ModelPipe1, ModelPipe2
from .nodes.tuning import SamplerCustomAdvanced_Pipe, AIO_Tuner, AIO_Tuner_Pipe, Beta_Config, LMS_Config, BasicAdvScheduler, stopipe
from .nodes.custom_nodes__sd_dynamic_thresholding import DynamicThresholding, DynamicThresholdingBasic
from .nodes.cond import CLIPTextEncode_Pipe
from .nodes.pysed import SedOnString
from .nodes.str_manipulation import str_str, str_str_str_str
from .nodes.modelinfo import get_lora_metadata
from .nodes.loaders import NoModel_CkptLoader


NODE_CLASS_MAPPINGS = {
    "Node_BOOL": Node_BOOL,
    "Node_INT": Node_INT,
    "Node_Float": Node_Float,
    "Node_String": Node_String,
    "Node_StringMultiline": Node_StringMultiline,
    "BooleanToPipe": BooleanToPipe,
    "BooleanFromPipe": BooleanFromPipe,
    "ExpMath": ExpMath,
    "ExpMathDual": ExpMathDual,
    "ExpMathQuad": ExpMathQuad,
    "EmptyLatentSize": EmptyLatentSize,
    "EmptyLatentSize64": EmptyLatentSize64,
    "SamplerSel": SamplerSel,
    "SchedulerSel": SchedulerSel,
    "LoraFluxParams": LoraFluxParams,
    "LoadUnetAndClip": LoadUnetAndClip,
    "UnetClipLoraLoader": UnetClipLoraLoader,
    "UnetClipLoraLoaderBasic": UnetClipLoraLoaderBasic,
    "CkptPipe": CkptPipe,
    "ModelPipe1": ModelPipe1,
    "ModelPipe2": ModelPipe2,
    "AIO_Tuner": AIO_Tuner,
    "AIO_Tuner_Pipe": AIO_Tuner_Pipe,
    "SamplerCustomAdvanced_Pipe": SamplerCustomAdvanced_Pipe,
    "Beta_Config": Beta_Config,
    "LMS_Config": LMS_Config,
    "BasicAdvScheduler": BasicAdvScheduler,
    "stopipe": stopipe,
    "DynamicThresholding": DynamicThresholding,
    "DynamicThresholdingBasic": DynamicThresholdingBasic,
    "CLIPTextEncode_Pipe": CLIPTextEncode_Pipe,
    "SedOnString": SedOnString,
    "str_str": str_str,
    "str_str_str_str": str_str_str_str,
    "get_lora_metadata": get_lora_metadata,
    "NoModel_CkptLoader": NoModel_CkptLoader,
}

prefix = '🛸 '
NODE_DISPLAY_NAME_MAPPINGS = {
    "Node_BOOL": prefix + "BOOL",
    "Node_INT": prefix + "INT",
    "Node_Float": prefix + "Float",
    "Node_String": prefix + "String",
    "Node_StringMultiline": prefix + "StringMultiline",
    "BooleanToPipe": prefix + "BooleanToPipe",
    "BooleanFromPipe": prefix + "BooleanFromPipe",
    "ExpMath": prefix + "ExpMath",
    "ExpMathDual": prefix + "ExpMathDual",
    "ExpMathQuad": prefix + "ExpMathQuad",
    "EmptyLatentSize": prefix + "EmptyLatentSize",
    "EmptyLatentSize64": prefix + "EmptyLatentSize64",
    "SamplerSel": prefix + "SamplerSel",
    "SchedulerSel": prefix + "SchedulerSel",
    "LoraFluxParams": prefix + "LoraFluxParams",
    "LoadUnetAndClip": prefix + "LoadUnetAndClip",
    "UnetClipLoraLoader": prefix + "UnetClipLoraLoader",
    "UnetClipLoraLoaderBasic": prefix + "UnetClipLoraLoaderBasic",
    "CkptPipe": prefix + "CkptPipe",
    "ModelPipe1": prefix + ">ModelPipe",
    "ModelPipe2": prefix + "<ModelPipe",
    "BasicAdvScheduler": prefix + "BasicAdvScheduler",
    "Beta_Config": prefix + "Beta_Config",
    "LMS_Config": prefix + "LMS_Config",
    "AIO_Tuner": prefix + "AIO_Tuner",
    "AIO_Tuner_Pipe": prefix + "AIO_Tuner_Pipe",
    "SamplerCustomAdvanced_Pipe": prefix + "SamplerCustomAdvanced_Pipe",
    "stopipe": prefix + "stopipe",
    "DynamicThresholding": prefix + "DynamicThresholding",
    "DynamicThresholdingBasic": prefix + "DynamicThresholdingBasic",
    "CLIPTextEncode_Pipe": prefix + "CLIPTextEncode_Pipe",
    "SedOnString": prefix + "SedOnString",
    "str_str": prefix + "str_str",
    "str_str_str_str": prefix + "str_str_str_str",
    "get_lora_metadata": prefix + "get_lora_metadata",
    "NoModel_CkptLoader": prefix + "NoModel_CkptLoader",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

WEB_DIRECTORY = "./web"