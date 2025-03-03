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


class CATEGORY(Enum):
  MAIN = "🛸KurtHokke"
  UTILS = "/Utils"
  MATH = "/Math"
  MISC = "/Misc"
