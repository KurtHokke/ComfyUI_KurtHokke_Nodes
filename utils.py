'''
    !DISCLAIMER! I'm very new to programming and I've been heavily inspired by following.
https://github.com/crystian/ComfyUI-Crystools
https://github.com/cubiq/ComfyUI_essentials
  Many thanks goes to these awesome developers!
'''
from enum import Enum
import sys
import contextlib
import torch

FLOAT = ("FLOAT", {"default": 1,
                   "min": -sys.float_info.max,
                   "max": sys.float_info.max,
                   "step": 0.01})

BOOLEAN = ("BOOLEAN", {"default": True})
BOOLEAN_FALSE = ("BOOLEAN", {"default": False})

INT = ("INT", {"default": 1,
               "min": -sys.maxsize,
               "max": sys.maxsize,
               "step": 1})

STRING = ("STRING", {"default": ""})

STRING_ML = ("STRING", {"multiline": True, "default": ""})

STRING_WIDGET = ("STRING", {"forceInput": True})

JSON_WIDGET = ("JSON", {"forceInput": True})

METADATA_RAW = ("METADATA_RAW", {"forceInput": True})

class AnyType(str):
  """A special class that is always equal in not equal comparisons. Credit to pythongosssss"""
  def __eq__(self, _) -> bool:
      return True
  def __ne__(self, __value: object) -> bool:
      return False

any = AnyType("*")


def parse_string_to_list(s):
    elements = s.split(',')
    result = []
    """Stolen from https://github.com/cubiq/ComfyUI_essentials"""
    def parse_number(s):
        try:
            if '.' in s:
                return float(s)
            else:
                return int(s)
        except ValueError:
            return 0

    def decimal_places(s):
        if '.' in s:
            return len(s.split('.')[1])
        return 0

    for element in elements:
        element = element.strip()
        if '...' in element:
            start, rest = element.split('...')
            end, step = rest.split('+')
            decimals = decimal_places(step)
            start = parse_number(start)
            end = parse_number(end)
            step = parse_number(step)
            current = start
            if (start > end and step > 0) or (start < end and step < 0):
                step = -step
            while current <= end:
                result.append(round(current, decimals))
                current += step
        else:
            result.append(round(parse_number(element), decimal_places(element)))

    return result


def get_weight_dtype_inputs():
    return {
        "weight_dtype": (
            [
                "default",
                "float32",
                "float64",
                "bfloat16",
                "float16",
                "fp8_e4m3fn",
                "fp8_e4m3fn_fast",
                "fp8_e5m2",
            ],
        ),
    }
def parse_weight_dtype(model_options, weight_dtype):
    dtype = {
        "float32": torch.float32,
        "float64": torch.float64,
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "fp8_e4m3fn": torch.float8_e4m3fn,
        "fp8_e4m3fn_fast": torch.float8_e4m3fn,
        "fp8_e5m2": torch.float8_e5m2,
    }.get(weight_dtype, None)
    if dtype is not None:
        model_options["dtype"] = dtype
    if weight_dtype == "fp8_e4m3fn_fast":
        model_options["fp8_optimizations"] = True
    return model_options

@contextlib.contextmanager
def disable_load_models_gpu():
    def foo(*args, **kwargs):
        pass

    from comfy import model_management

    with unittest.mock.patch.object(model_management, "load_models_gpu", foo):
        yield

MODEL_TYPES = ["FLUX", "SDXL"]
CONCAT_WHERE = ["<", ">"]

class CATEGORY(Enum):
    MAIN = "🛸KurtHokke"
