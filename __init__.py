
from .utils import CATEGORY
from .nodes.util_nodes import Node_BOOL, Node_INT, Node_Float, Node_String, Node_StringMultiline, Node_RandomRange
from .nodes.util_nodes import CompareTorch, DoOperations, TensorStats, TensorToConditioning, DetailDaemonPrimitive
from .nodes.debugany import DebugAny
from .nodes.debugany2 import DebugAny2, DebugAny3
from .nodes.create_instance import CreateInstance
from .nodes.pipe import BooleanToPipe, BooleanFromPipe
from .nodes.math import ExpMath, ExpMathDual, ExpMathQuad
from .nodes.misc import EmptyLatentSize, EmptyLatentSize64, SchedulerSel, SamplerSel
#from .nodes.misc import LoraFluxParams
from .nodes.models import LoadUnetAndClip, UnetClipLoraLoader, UnetClipLoraLoaderBasic, CkptPipe, ModelPipe1, ModelPipe2
from .nodes.tuning import SamplerCustomAdvanced_Pipe, AIO_Tuner_Pipe
from .nodes.extraopts import MergeExtraOpts, VAE_ExtraOpts, COND_ExtraOpts, batchsize_ExtraOpts, SEED_ExtraOpts, NoNegExtraOpts, COND_ExtraOpts_2, COND_SET_STRENGTH_ExtraOpts
from .nodes.extraopts import ViewExtraOpts, MultiplyTensorsExtraOpts, TensorsExtraOpts, LoraNamesExtraOpts, LoraSettingsExtraOpts
from .nodes.extraopts import KeyframeExtraOpts
from .nodes.custom_nodes__sd_dynamic_thresholding import DynamicThresholding, DynamicThresholdingBasic
#from .nodes.cond import mycombine, splitcond
from .nodes.cond import ChainTextEncode, ApplyCondsExtraOpts, ChainText
from .nodes.pysed import SedOnString
from .nodes.pyre import re_sub_str
from .nodes.str_manipulation import str_str, str_str_str_str
from .nodes.modelinfo import get_lora_metadata
from .nodes.loaders import NoModel_CkptLoader
from .nodes.experimental_hooks import CreateHookLoraTestSelf, CreateHookWithKF, SetModelHooksOnCond, expHook
from .nodes.AIO import AIO, extGSSS
#from .nodes.debug import ExecutePythonNode
#from .nodes.bashnode import BashScriptNode
#from .nodes.inspectnode import InspectNode



prefix = CATEGORY.prefix.value

NODE_CLASS_MAPPINGS = {
    "Node_BOOL": Node_BOOL,
    "Node_INT": Node_INT,
    "Node_Float": Node_Float,
    "Node_String": Node_String,
    "Node_StringMultiline": Node_StringMultiline,
    "Node_RandomRange": Node_RandomRange,
    "CompareTorch": CompareTorch,
    "DoOperations": DoOperations,
    "TensorStats": TensorStats,
    "TensorToConditioning": TensorToConditioning,
    "DetailDaemonPrimitive": DetailDaemonPrimitive,
    "DebugAny": DebugAny,
    "DebugAny2": DebugAny2,
    "DebugAny3": DebugAny3,
    "CreateInstance": CreateInstance,
    "BooleanToPipe": BooleanToPipe,
    "BooleanFromPipe": BooleanFromPipe,
    "ExpMath": ExpMath,
    "ExpMathDual": ExpMathDual,
    "ExpMathQuad": ExpMathQuad,
    "EmptyLatentSize": EmptyLatentSize,
    "EmptyLatentSize64": EmptyLatentSize64,
    "SamplerSel": SamplerSel,
    "SchedulerSel": SchedulerSel,
    #"LoraFluxParams": LoraFluxParams,
    "LoadUnetAndClip": LoadUnetAndClip,
    "UnetClipLoraLoader": UnetClipLoraLoader,
    "UnetClipLoraLoaderBasic": UnetClipLoraLoaderBasic,
    "CkptPipe": CkptPipe,
    "ModelPipe1": ModelPipe1,
    "ModelPipe2": ModelPipe2,
    "AIO_Tuner_Pipe": AIO_Tuner_Pipe,
    "SamplerCustomAdvanced_Pipe": SamplerCustomAdvanced_Pipe,
    "ViewExtraOpts": ViewExtraOpts,
    "MergeExtraOpts": MergeExtraOpts,
    "VAE_ExtraOpts": VAE_ExtraOpts,
    "COND_ExtraOpts": COND_ExtraOpts,
    "COND_ExtraOpts_2": COND_ExtraOpts_2,
    "COND_SET_STRENGTH_ExtraOpts": COND_SET_STRENGTH_ExtraOpts,
    "MultiplyTensorsExtraOpts": MultiplyTensorsExtraOpts,
    "TensorsExtraOpts": TensorsExtraOpts,
    "batchsize_ExtraOpts": batchsize_ExtraOpts,
    "SEED_ExtraOpts": SEED_ExtraOpts,
    "NoNegExtraOpts": NoNegExtraOpts,
    "LoraNamesExtraOpts": LoraNamesExtraOpts,
    "LoraSettingsExtraOpts": LoraSettingsExtraOpts,
    "KeyframeExtraOpts": KeyframeExtraOpts,
    "DynamicThresholding": DynamicThresholding,
    "DynamicThresholdingBasic": DynamicThresholdingBasic,
    "ChainTextEncode": ChainTextEncode,
    "ChainText": ChainText,
    "SedOnString": SedOnString,
    "re_sub_str": re_sub_str,
    "str_str": str_str,
    "str_str_str_str": str_str_str_str,
    "get_lora_metadata": get_lora_metadata,
    "NoModel_CkptLoader": NoModel_CkptLoader,
    #"ExecutePythonNode": ExecutePythonNode,
    #"BashScriptNode": BashScriptNode,
    #"mycombine": mycombine,
    #"splitcond": splitcond,
    "ApplyCondsExtraOpts": ApplyCondsExtraOpts,
    #"InspectNode": InspectNode,
    "CreateHookLoraTestSelf": CreateHookLoraTestSelf,
    "CreateHookWithKF": CreateHookWithKF,
    "SetModelHooksOnCond": SetModelHooksOnCond,
    "expHook": expHook,
    "AIO": AIO,
    "extGSSS": extGSSS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Node_BOOL": prefix + "BOOL",
    "Node_INT": prefix + "INT",
    "Node_Float": prefix + "Float",
    "Node_String": prefix + "String",
    "Node_StringMultiline": prefix + "StringMultiline",
    "Node_RandomRange": prefix + "RandomRange",
    "CompareTorch": prefix + "CompareTorch",
    "DoOperations": prefix + "DoOperations",
    "TensorStats": prefix + "TensorStats",
    "TensorToConditioning": prefix + "TensorToConditioning",
    "DetailDaemonPrimitive": prefix + "DetailDaemonPrimitive",
    "DebugAny": prefix + "DebugAny",
    "DebugAny2": prefix + "DebugAny2",
    "DebugAny3": prefix + "DebugAny3",
    "CreateInstance": prefix + "CreateInstance",
    "BooleanToPipe": prefix + "BooleanToPipe",
    "BooleanFromPipe": prefix + "BooleanFromPipe",
    "ExpMath": prefix + "ExpMath",
    "ExpMathDual": prefix + "ExpMathDual",
    "ExpMathQuad": prefix + "ExpMathQuad",
    "EmptyLatentSize": prefix + "EmptyLatentSize",
    "EmptyLatentSize64": prefix + "EmptyLatentSize64",
    "SamplerSel": prefix + "SamplerSel",
    "SchedulerSel": prefix + "SchedulerSel",
    #"LoraFluxParams": prefix + "LoraFluxParams",
    "LoadUnetAndClip": prefix + "LoadUnetAndClip",
    "UnetClipLoraLoader": prefix + "UnetClipLoraLoader",
    "UnetClipLoraLoaderBasic": prefix + "UnetClipLoraLoaderBasic",
    "CkptPipe": prefix + "CkptPipe",
    "ModelPipe1": prefix + ">ModelPipe",
    "ModelPipe2": prefix + "<ModelPipe",
    "AIO_Tuner_Pipe": prefix + "AIO_Tuner_Pipe",
    "SamplerCustomAdvanced_Pipe": prefix + "SamplerCustomAdvanced_Pipe",
    "ViewExtraOpts": prefix + "ViewExtraOpts",
    "MergeExtraOpts": prefix + "MergeExtraOpts",
    "VAE_ExtraOpts": prefix + "VAE_ExtraOpts",
    "COND_ExtraOpts": prefix + "COND_ExtraOpts",
    "COND_ExtraOpts_2": prefix + "COND_ExtraOpts_2",
    "COND_SET_STRENGTH_ExtraOpts": prefix + "COND_SET_STRENGTH_ExtraOpts",
    "MultiplyTensorsExtraOpts": prefix + "MultiplyTensorsExtraOpts",
    "TensorsExtraOpts": prefix + "TensorsExtraOpts",
    "batchsize_ExtraOpts": prefix + "batchsize_ExtraOpts",
    "SEED_ExtraOpts": prefix + "SEED_ExtraOpts",
    "NoNegExtraOpts": prefix + "NoNegExtraOpts",
    "LoraNamesExtraOpts": prefix + "LoraNamesExtraOpts",
    "LoraSettingsExtraOpts": prefix + "LoraSettingsExtraOpts",
    "KeyframeExtraOpts": prefix + "KeyframeExtraOpts",
    "DynamicThresholding": prefix + "DynamicThresholding",
    "DynamicThresholdingBasic": prefix + "DynamicThresholdingBasic",
    "ChainTextEncode": prefix + "ChainTextEncode",
    "ChainText": prefix + "ChainText",
    "SedOnString": prefix + "SedOnString",
    "re_sub_str": prefix + "re_sub_str",
    "str_str": prefix + "str_str",
    "str_str_str_str": prefix + "str_str_str_str",
    "get_lora_metadata": prefix + "get_lora_metadata",
    "NoModel_CkptLoader": prefix + "NoModel_CkptLoader",
    #"ExecutePythonNode": prefix + "ExecutePythonNode",
    #"BashScriptNode": prefix + "BashScriptNode",
    #"mycombine": prefix + "mycombine",
    #"splitcond": prefix + "splitcond",
    "ApplyCondsExtraOpts": prefix + "ApplyCondsExtraOpts",
    #"InspectNode": prefix + "InspectNode",
    "CreateHookLoraTestSelf": prefix + "CreateHookLoraTestSelf",
    "CreateHookWithKF": prefix + "CreateHookWithKF",
    "SetModelHooksOnCond": prefix + "SetModelHooksOnCond",
    "expHook": prefix + "expHook",
    "AIO": prefix + "AIO",
    "extGSSS": prefix + "extGSSS",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

WEB_DIRECTORY = "./web"

