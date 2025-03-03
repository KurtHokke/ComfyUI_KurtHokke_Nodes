'''
    !DISCLAIMER! I'm very new to programming and I've been heavily inspired by following.
https://github.com/crystian/ComfyUI-Crystools
https://github.com/cubiq/ComfyUI_essentials
  Many thanks goes to these awesome developers!
'''
from ..utils import any, BOOLEAN, INT, FLOAT, STRING
from ..names import CATEGORY
import math
import torch
import time

class BooleanToPipe:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "boolean_1": BOOLEAN,
                "boolean_2": BOOLEAN,
                "boolean_3": BOOLEAN,
                "boolean_4": BOOLEAN,
            }
        }

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value
    RETURN_TYPES = ("BoolPipe",)

    FUNCTION = "execute"

    def execute(self, boolean_1=True, boolean_2=True, boolean_3=True, boolean_4=True):
        # Create a list to hold the boolean values
        BoolPipeMod = []

        # Append the boolean values directly
        BoolPipeMod.append(boolean_1)
        BoolPipeMod.append(boolean_2)
        BoolPipeMod.append(boolean_3)
        BoolPipeMod.append(boolean_4)

        # Return the list as separate boolean outputs
        return (BoolPipeMod,)

class BooleanFromPipe:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "BoolPipe": (any,),
            },
            "optional": {
            }
        }

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value
    RETURN_TYPES = ("BOOLEAN", "BOOLEAN", "BOOLEAN", "BOOLEAN",)
    RETURN_NAMES = ("boolean_1", "boolean_2", "boolean_3", "boolean_4",)

    FUNCTION = "execute"

    def execute(self, BoolPipe=None, ):
        boolean_1, boolean_2, boolean_3, boolean_4, = BoolPipe
        return boolean_1, boolean_2, boolean_3, boolean_4


class ExpMath:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "a": (any, { "default": 0.0 }),
                "b": (any, { "default": 0.0 }),
                "c": (any, { "default": 0.0 }),
            },
            "required": {
                "value": ("STRING", { "multiline": False, "default": "" }),
            },
        }

    CATEGORY = CATEGORY.MAIN.value + CATEGORY.MATH.value
    RETURN_TYPES = ("INT", "FLOAT", )
    
    FUNCTION = "execute"
    
    def execute(self, value, a = 0.0, b = 0.0, c = 0.0, d = 0.0):
        import ast
        import operator as op

        h, w = 0.0, 0.0
        if hasattr(a, 'shape'):
            a = list(a.shape)
        if hasattr(b, 'shape'):
            b = list(b.shape)
        if hasattr(c, 'shape'):
            c = list(c.shape)
        if hasattr(d, 'shape'):
            d = list(d.shape)

        if isinstance(a, str):
            a = float(a)
        if isinstance(b, str):
            b = float(b)
        if isinstance(c, str):
            c = float(c)
        if isinstance(d, str):
            d = float(d)
        
        operators = {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.FloorDiv: op.floordiv,
            ast.Pow: op.pow,
            #ast.BitXor: op.xor,
            #ast.BitOr: op.or_,
            #ast.BitAnd: op.and_,
            ast.USub: op.neg,
            ast.Mod: op.mod,
            ast.Eq: op.eq,
            ast.NotEq: op.ne,
            ast.Lt: op.lt,
            ast.LtE: op.le,
            ast.Gt: op.gt,
            ast.GtE: op.ge,
            ast.And: lambda x, y: x and y,
            ast.Or: lambda x, y: x or y,
            ast.Not: op.not_
        }

        op_functions = {
            'min': min,
            'max': max,
            'round': round,
            'sum': sum,
            'len': len,
        }

        def eval_(node):
            if isinstance(node, ast.Num): # number
                return node.n
            elif isinstance(node, ast.Name): # variable
                if node.id == "a":
                    return a
                if node.id == "b":
                    return b
                if node.id == "c":
                    return c
                if node.id == "d":
                    return d
            elif isinstance(node, ast.BinOp): # <left> <operator> <right>
                return operators[type(node.op)](eval_(node.left), eval_(node.right))
            elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
                return operators[type(node.op)](eval_(node.operand))
            elif isinstance(node, ast.Compare):  # comparison operators
                left = eval_(node.left)
                for op, comparator in zip(node.ops, node.comparators):
                    if not operators[type(op)](left, eval_(comparator)):
                        return 0
                return 1
            elif isinstance(node, ast.BoolOp):  # boolean operators (And, Or)
                values = [eval_(value) for value in node.values]
                return operators[type(node.op)](*values)
            elif isinstance(node, ast.Call): # custom function
                if node.func.id in op_functions:
                    args =[eval_(arg) for arg in node.args]
                    return op_functions[node.func.id](*args)
            elif isinstance(node, ast.Subscript): # indexing or slicing
                value = eval_(node.value)
                if isinstance(node.slice, ast.Constant):
                    return value[node.slice.value]
                else:
                    return 0
            else:
                return 0

        result = eval_(ast.parse(value, mode='eval').body)

        if math.isnan(result):
            result = 0.0
        
        return (round(result), result, )

class ExpMathDual:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "a": (any, { "default": 0.0 }),
                "b": (any, { "default": 0.0 }),
                "c": (any, { "default": 0.0 }),
                "d": (any, { "default": 0.0 }),
            },
            "required": {
                "value_1": ("STRING", { "multiline": False, "default": "" }),
                "value_2": ("STRING", { "multiline": False, "default": "" }),
            },
        }
    
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.MATH.value
    RETURN_TYPES = ("INT", "FLOAT", "INT", "FLOAT", )
    RETURN_NAMES = ("int_1", "float_1", "int_2", "float_2" )
    
    FUNCTION = "execute"

    def execute(self, value_1, value_2, a = 0.0, b = 0.0, c = 0.0, d = 0.0):
        return SimpleMath().execute(value_1, a, b, c, d) + SimpleMath().execute(value_2, a, b, c, d)