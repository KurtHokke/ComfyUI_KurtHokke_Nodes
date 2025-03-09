'''
    !DISCLAIMER! I'm very new to programming and I've been heavily inspired by following.
https://github.com/crystian/ComfyUI-Crystools
https://github.com/cubiq/ComfyUI_essentials
  Many thanks goes to these awesome developers!
'''
from enum import Enum

prefix = '🛸 '

# IMPORTANT DON'T CHANGE THE 'NAME' AND 'TYPE' OF THE ENUMS, IT WILL BREAK THE COMPATIBILITY!
# remember: NAME is for search, DESC is for contextual
class CLASSES(Enum):
    BOOLEANTOPIPE_NAME = 'Boolean To Pipe'
    BOOLEANTOPIPE_DESC = prefix + 'Boolean To Pipe'
    BOOLEANFROMPIPE_NAME = 'Boolean From Pipe'
    BOOLEANFROMPIPE_DESC = prefix + 'Boolean From Pipe'
    EXPMATH_NAME = 'ExpMath'
    EXPMATH_DESC = prefix + 'ExpMath'
    EXPMATHDUAL_NAME = 'ExpMathDual'
    EXPMATHDUAL_DESC = prefix + 'ExpMathDual'
    EXPMATHQUAD_NAME = 'ExpMathQuad'
    EXPMATHQUAD_DESC = prefix + 'ExpMathQuad'
    EMPTYLATENTSIZE_NAME = 'EmptyLatentSize'
    EMPTYLATENTSIZE_DESC = prefix + 'EmptyLatentSize'
    EMPTYLATENTSIZE64_NAME = 'EmptyLatentSize64'
    EMPTYLATENTSIZE64_DESC = prefix + 'EmptyLatentSize64'
    SAMPLERSEL_NAME = 'SamplerSel'
    SAMPLERSEL_DESC = prefix + 'SamplerSel'
    SCHEDULERSEL_NAME = 'SchedulerSel'
    SCHEDULERSEL_DESC = prefix + 'SchedulerSel'
    LORAFLUXPARAMS_NAME = 'LoraFluxParams'
    LORAFLUXPARAMS_DESC = prefix + 'LoraFluxParams'
    LOADUNETANDCLIP_NAME = 'LoadUnetAndClip'
    LOADUNETANDCLIP_DESC = prefix + 'LoadUnetAndClip'
    UNETCLIPLORALOADER_NAME = 'UnetClipLoraLoader'
    UNETCLIPLORALOADER_DESC = prefix + 'UnetClipLoraLoader'
    UNETCLIPLORALOADERBASIC_NAME = 'UnetClipLoraLoaderBasic'
    UNETCLIPLORALOADERBASIC_DESC = prefix + 'UnetClipLoraLoaderBasic'
    CKPTPIPE_NAME = 'CkptPipe'
    CKPTPIPE_DESC = prefix + 'CkptPipe'
    MODELPIPE1_NAME = '>ModelPipe'
    MODELPIPE1_DESC = prefix + '>ModelPipe'
    MODELPIPE2_NAME = '<ModelPipe'
    MODELPIPE2_DESC = prefix + '<ModelPipe'
    BASICADVSCHEDULER_NAME = 'BasicAdvScheduler'
    BASICADVSCHEDULER_DESC = prefix + 'BasicAdvScheduler'
    BETA_CONFIG_NAME = 'S_BetaConfig'
    BETA_CONFIG_DESC = prefix + 'S_BetaConfig'
    LMS_CONFIG_NAME = 'LMS_Config'
    LMS_CONFIG_DESC = prefix + 'LMS_Config'
    AIO_TUNER_NAME = 'AIO_Tuner'
    AIO_TUNER_DESC = prefix + 'AIO_Tuner'
    AIO_TUNER_PIPE_NAME = 'AIO_Tuner_Pipe'
    AIO_TUNER_PIPE_DESC = prefix + 'AIO_Tuner_Pipe'
    SAMPLERCUSTOMADVANCED_PIPE_NAME = 'SamplerCustomAdvanced_Pipe'
    SAMPLERCUSTOMADVANCED_PIPE_DESC = prefix + 'SamplerCustomAdvanced_Pipe'
    STOPIPE_NAME = 'stopipe'
    STOPIPE_DESC = prefix + 'stopipe'
    


class CATEGORY(Enum):
    MAIN = "🛸KurtHokke"
    UTILS = "/Utils"
    MATH = "/Math"
    LOADERS = "/Loaders"
    PATCH = "/Patch"
    SAMPLING = "/Sampling"
    MISC = "/Misc"
    TUNING = "/Tuning"

MODEL_TYPES = ["FLUX", "SDXL"]