'''
    !DISCLAIMER! I'm very new to programming and I've been heavily inspired by following.
https://github.com/crystian/ComfyUI-Crystools
https://github.com/cubiq/ComfyUI_essentials
  Many thanks goes to these awesome developers!
'''
from .names import CLASSES
from .nodes.pipe import BooleanToPipe, BooleanFromPipe
from .nodes.math import ExpMath, ExpMathDual, ExpMathQuad
from .nodes.misc import EmptyLatentSize, EmptyLatentSize64


NODE_CLASS_MAPPINGS = {
  CLASSES.BOOLEANTOPIPE_NAME.value: BooleanToPipe,
  CLASSES.BOOLEANFROMPIPE_NAME.value: BooleanFromPipe,
  CLASSES.EXPMATH_NAME.value: ExpMath,
  CLASSES.EXPMATHDUAL_NAME.value: ExpMathDual,
  CLASSES.EXPMATHQUAD_NAME.value: ExpMathQuad,
  CLASSES.EMPTYLATENTSIZE_NAME.value: EmptyLatentSize,
  CLASSES.EMPTYLATENTSIZE64_NAME.value: EmptyLatentSize64,
}

NODE_DISPLAY_NAME_MAPPINGS = {
  CLASSES.BOOLEANTOPIPE_NAME.value: CLASSES.BOOLEANTOPIPE_DESC.value,
  CLASSES.BOOLEANFROMPIPE_NAME.value: CLASSES.BOOLEANFROMPIPE_DESC.value,
  CLASSES.EXPMATH_NAME.value: CLASSES.EXPMATH_DESC.value,
  CLASSES.EXPMATHDUAL_NAME.value: CLASSES.EXPMATHDUAL_DESC.value,
  CLASSES.EXPMATHQUAD_NAME.value: CLASSES.EXPMATHQUAD_DESC.value,
  CLASSES.EMPTYLATENTSIZE_NAME.value: CLASSES.EMPTYLATENTSIZE_DESC.value,
  CLASSES.EMPTYLATENTSIZE64_NAME.value: CLASSES.EMPTYLATENTSIZE64_DESC.value,
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]