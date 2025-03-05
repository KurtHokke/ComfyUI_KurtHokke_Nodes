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
    LORAHOOKSCHEDULERBASIC_NAME = 'LoraHookSchedulerBasic'
    LORAHOOKSCHEDULERBASIC_DESC = prefix + 'LoraHookSchedulerBasic'
    CKPTPIPE_NAME = 'CkptPipe'
    CKPTPIPE_DESC = prefix + 'CkptPipe'
    MODELPIPE1_NAME = '>ModelPipe'
    MODELPIPE1_DESC = prefix + '>ModelPipe'
    MODELPIPE2_NAME = '<ModelPipe'
    MODELPIPE2_DESC = prefix + '<ModelPipe'
#    MODELPIPEHOOKS_NAME = 'ModelPipeHooks'
#    MODELPIPEHOOKS_DESC = prefix + 'ModelPipeHooks'


class CATEGORY(Enum):
  MAIN = "🛸KurtHokke"
  UTILS = "/Utils"
  MATH = "/Math"
  LOADERS = "/Loaders"
  PATCH = "/Patch"
  SAMPLING = "/Sampling"
  MISC = "/Misc"
