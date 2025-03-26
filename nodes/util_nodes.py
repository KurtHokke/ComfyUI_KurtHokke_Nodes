from khn.utils import CATEGORY, any, logger, OPERATIONS, prefix
from khn.helpers import DataHandler
from comfy.comfy_types import *


class Node_BOOL:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "value": ("BOOLEAN", {"default": True}),
            }
        }
    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("value",)
    FUNCTION = "get_value"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

    def get_value(self, value):
        return (value,)

class Node_INT:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "value": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("value",)
    FUNCTION = "get_value"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

    def get_value(self, value):
        return (value,)

class Node_Float:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "value": ("FLOAT", {"default": 0.0, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff, "step": 0.0001}),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("value",)
    FUNCTION = "get_value"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

    def get_value(self, value):
        return (value,)

class Node_String:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "_": ("STRING", {"default": '', "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "passtring"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

    def passtring(self, _):
        string = _
        return (string, )

class Node_StringMultiline:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"default": "", "multiline": True}),
            }
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "stringify"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

    def stringify(self, string):
        return (string, )

class Node_RandomRange:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "min": ("FLOAT", {"default": 0.00, "min": -9999999999.00, "max": 9999999999.00, "step": 0.001}),
                "max": ("FLOAT", {"default": 10.00, "min": -9999999999.00, "max": 9999999999.00, "step": 0.001}),
            }
        }
    RETURN_TYPES = ("INT", "FLOAT")
    FUNCTION = "randomrange"
    OUTPUT_NODE = True
    IS_CHANGED = True
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

    def randomrange(self, min, max):
        import random
        random_float = random.uniform(min, max)
        random_int = int(random_float)
        return random_int, random_float

class CompareTorch:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "a": (any , ),
                "b": (any , ),
            }
        }
    RETURN_TYPES = (any, any,)
    RETURN_NAMES = ("boolean", "*",)
    FUNCTION = "compare"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

    def unlist(self, nested):
        if not isinstance(nested, (list, tuple)):
            return [nested]

        flattened = []
        for item in nested:
            flattened.extend(self.unlist(item))
        return flattened

    def compare(self, a, b):
        import torch

        logger.debug(f"{a}, {b}")
        if isinstance(a, list):
            logger.debug(f"unlisting {a}")
            a = self.unlist(a)[0]
        if isinstance(b, list):
            logger.debug(f"unlisting {b}")
            b = self.unlist(b)[0]
        logger.debug(f"type(a) == {type(a)}\ntype(b) == {type(b)}")
        if not isinstance(a, torch.Tensor) or not isinstance(b, torch.Tensor):
            exeptionstr = f"type(a) = {type(a)}, type(b) = {type(b)}\nCannot compare as both are not tensors\n{a}\n{b}"
            return (exeptionstr, exeptionstr)
        elif torch.equal(a, b):
            return (True, f"a == b ==\n{a}")
        else:
            # Find element-wise differences if tensors are not equal
            diff_indices = (a != b).nonzero(as_tuple=True)
            differences = [f"At index {index}: a = {val1}, b = {val2}"
                           for index, val1, val2 in zip(diff_indices[0], a[diff_indices], b[diff_indices])]
            return (False, len(differences))
            #return ("\n".join(differences) or "Tensors have the same shape and elements.")

class DoOperations:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "operation": (OPERATIONS,)
            },
            "optional": {
                "a": (any , ),
                "b": (any , ),
                "c": (any , ),
            }
        }
    RETURN_TYPES = (any, "STRING", any, "STRING", any, "STRING",)
    RETURN_NAMES = ("a", "a_str", "b", "b_str", "c", "c_str",)
    FUNCTION = "execute"
    IS_CHANGED = True

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

    def execute(self, operation, a=None, b=None, c=None):
        if operation == "unlist":
            results = []
            for data in [a, b, c]:
                if data is not None:
                    results.append(DataHandler.flatten(data)[0])
                else:
                    results.append(None)

            return (results[0], str(results[0]), results[1], str(results[1]), results[2], str(results[2]))
        elif operation == "tensors*c":
            if c is not None and a is not None and b is not None:
                a_result = DataHandler.multiply_tensors(a, left_f=b, right_f=c)
                return (a_result, str(a_result), b, str(b), c, float(c))

class TensorStats:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tensor": (any , ),
            }
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_stats"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

    def get_stats(self, tensor):
        import torch
        if isinstance(tensor, list) or isinstance(tensor, tuple) or isinstance(tensor, torch.Tensor):
            if isinstance(tensor, (list, tuple)):
                tensor = DataHandler.flatten(tensor)[0]
                logger.debug(f"flattened tensor:\n{tensor}")
                if isinstance(tensor, torch.Tensor):
                    t_shape = tensor.shape
                    t_size = tensor.size()
                    t_dtype = tensor.dtype
                    t_device = tensor.device
                    t_ndim = tensor.ndim
                    t_numel = tensor.numel()
                    t_min = tensor.min()
                    t_max = tensor.max()
                    t_mean = tensor.mean()
                    t_std = tensor.std()
                    t_isnan = tensor.isnan().any()
                    t_isinf = tensor.isinf().any()
                    stats = f"shape: {t_shape}\nsize: {t_size}\ndtype: {t_dtype}\ndevice: {t_device}\nndim: {t_ndim}\nnumel: {t_numel}\nmin: {t_min}\nmax: {t_max}\nmean: {t_mean}\nstd: {t_std}\nisnan: {t_isnan}\nisinf: {t_isinf}"
                    return (stats,)
                else:
                    return ("",)
            else:
                return ("",)
        else:
            return ("",)


class TensorToConditioning:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tensor": ("STRING", {
                    "multiline": True,
                    "default": "Paste conditioing tensor data here",
                    "defaultInput": False,
                }),
            }
        }
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "tensor_to_conditioning"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.CONDITIONING.value

    def tensor_to_conditioning(self, tensor):
        if isinstance(tensor, (list, tuple, str)):
            list_depth = DataHandler.nesting_depth(tensor)
            if list_depth == 2:
                import torch
                tensor = torch.Tensor(tensor)
                tensor = tensor.tolist()
                logger.debug(f"tensor: {tensor}")
                logger.debug(f"tensor: {tensor}")
                logger.debug(f"tensor: {tensor}")
                return (tensor,)
            else:
                logger.debug(f"tensors nesting depth is not 2, nested depth:{list_depth}\nmake sure the tensor is surrounded by brackets like: [[...]]",)
        else:
            logger.debug(f"INPUT IS NOT A LIST OR TUPLE: {type(tensor)}",)


class DetailDaemonPrimitive:

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "detail_amount": ("FLOAT", {"default": 0.1, "min": -5.0, "max": 5.0, "step": 0.01},),
                "start": ("FLOAT",{"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01},),
                "end": ("FLOAT",{"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01},),
                "bias": ("FLOAT",{"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01},),
                "exponent": ("FLOAT",{"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.05},),
                "start_offset": ("FLOAT",{"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01},),
                "end_offset": ("FLOAT",{"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01},),
                "fade": ("FLOAT",{"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05},),
                "smooth": ("BOOLEAN", {"default": True}),
                "cfg_scale_override": ("FLOAT",{"default": 0, "min": 0.0, "max": 100.0, "step": 0.5, "round": 0.01, "tooltip": "If set to 0, the sampler will automatically determine the CFG scale (if possible). Set to some other value to override.",},),
            }
        }
    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT", "BOOLEAN", "FLOAT",)
    RETURN_NAMES = ("detail_amount", "start", "end", "bias", "exponent", "start_offset", "end_offset", "fade", "smooth", "cfg_scale_override",)
    FUNCTION = "execute"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

    def execute(self, detail_amount, start, end, bias, exponent, start_offset, end_offset, fade, smooth, cfg_scale_override):
        return (detail_amount, start, end, bias, exponent, start_offset, end_offset, fade, smooth, cfg_scale_override)


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
}