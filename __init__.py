'''
    !DISCLAIMER! I'm very new to programming and I've been heavily inspired by following.
https://github.com/crystian/ComfyUI-Crystools
https://github.com/cubiq/ComfyUI_essentials
  Many thanks goes to these awesome developers!
'''
from enum import Enum
from .nodes.pipe import BooleanToPipe, BooleanFromPipe
from .nodes.math import ExpMath, ExpMathDual, ExpMathQuad
from .nodes.misc import EmptyLatentSize, EmptyLatentSize64, SchedulerSel, SamplerSel, LoraFluxParams
from .nodes.models import LoadUnetAndClip, UnetClipLoraLoader, UnetClipLoraLoaderBasic, CkptPipe, ModelPipe1, ModelPipe2
from .nodes.tuning import SamplerCustomAdvanced_Pipe, AIO_Tuner, AIO_Tuner_Pipe, Beta_Config, LMS_Config, BasicAdvScheduler, stopipe
#from .nodes.models import LoadUnetAndClip, UnetClipLoraLoader, UnetClipLoraLoaderBasic, CkptPipe, ModelPipe1, ModelPipe2, LoraHookSchedulerBasic, ModelPipeHooks



NODE_CLASS_MAPPINGS = {
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
}

prefix = '🛸 '
NODE_DISPLAY_NAME_MAPPINGS = {
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
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

WEB_DIRECTORY = "./web"