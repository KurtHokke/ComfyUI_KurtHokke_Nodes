'''
    !DISCLAIMER! I'm very new to programming and I've been heavily inspired by following.
https://github.com/crystian/ComfyUI-Crystools
  Many thanks goes to these awesome developers!
'''
from .nodes import BooleanToPipe, BooleanFromPipe
from .names import CLASSES

NODE_CLASS_MAPPINGS = {
  CLASSES.BOOLEANTOPIPE_NAME.value: BooleanToPipe,
  CLASSES.BOOLEANFROMPIPE_NAME.value: BooleanFromPipe,
}

NODE_DISPLAY_NAME_MAPPINGS = {
  CLASSES.BOOLEANTOPIPE_NAME.value: CLASSES.BOOLEANTOPIPE_DESC.value,
  CLASSES.BOOLEANFROMPIPE_NAME.value: CLASSES.BOOLEANFROMPIPE_DESC.value,
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]