from .loggers import get_logger
import comfy.sd
import torch

logger, log_all = get_logger("log_all")

class SampleAssembler:
    def __init__(self, models):
        self.models = []
        self.prompts = {
            "pos": [],
            "neg": [],
        }
        self.latent_opts = []
        self.latent_ch = 4
        self.extra_opts = None
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"

        self.update_models(models)

    def update_models(self, models=None):
        if self.models != models:
            self.models = models
            self.latent_ch = self.models[2].latent_channels

    def update_prompts(self, pos_prompts=None, neg_prompts=None):
        if self.prompts["pos"] != pos_prompts:
            self.prompts["pos"] = pos_prompts
        if self.prompts["neg"] != neg_prompts:
            self.prompts["neg"] = neg_prompts

    def get_latent(self, batch_size=1):
        latent = torch.zeros([batch_size, self.latent_ch, self.latent_opts[1] // 8, self.latent_opts[0] // 8], device=self.device)
        return ({"samples":latent}, )



class DataHandler:
    def is_instance_recursive(self, flattened_obj, obj_is=None):
        if obj_is is None:
            obj_is = {}
        for item in flattened_obj:
            recursive_obj_is = self.is_instance(item, obj_is=obj_is, start=False)
            obj_is = {**obj_is, **recursive_obj_is}
        return obj_is

    def is_instance(self, obj, obj_is=None, start=True):
        from torch import Tensor
        if obj_is is None and start is True:
            obj_is = {}
        if isinstance(obj, dict):
            obj_is = {**obj_is, "dict": True}
        if isinstance(obj, list):
            obj_is = {**obj_is, "list": True}
            flattened_obj = self.flatten(obj)
            item_types = self.is_instance_recursive(flattened_obj, obj_is)
            obj_is = {**obj_is, **item_types}

        if isinstance(obj, tuple):
            obj_is = {**obj_is, "tuple": True}
            obj_len = len(obj)
            for i in range(obj_len):
                if isinstance(obj[i], list):
                    flattened_obj = self.flatten(obj[i])
                    item_types = self.is_instance_recursive(flattened_obj, obj_is)
                    obj_is = {**obj_is, **item_types}
                else:
                    item_types = self.is_instance(obj[i], obj_is=obj_is, start=False)
                    obj_is = {**obj_is, **item_types}
        if isinstance(obj, str):
            obj_is = {**obj_is, "str": True}
        if isinstance(obj, int):
            obj_is = {**obj_is, "int": True}
        if isinstance(obj, float):
            obj_is = {**obj_is, "float": True}
        if isinstance(obj, bool):
            obj_is = {**obj_is, "bool": True}
        if isinstance(obj, bytes):
            obj_is = {**obj_is, "bytes": True}
        if isinstance(obj, Tensor):
            obj_is = {**obj_is, "tensor": True}
        if obj_is == {}:
            obj_is = {**obj_is, "UNSOLVED_TYPE": True}

        return obj_is

    def flatten(self, nested):
        if not isinstance(nested, (list, tuple)):
            return [nested]
        flattened = []
        for item in nested:
            flattened.extend(self.flatten(item))
        return flattened

    @staticmethod
    def nesting_depth(seq):
        from collections.abc import Sequence
        from itertools import chain, count
        if isinstance(seq, tuple):
            logger.info(f"tuple detected: {type(seq)}")
            seq = seq[0]
            logger.info(f"Should now be list: {type(seq)}")
        if isinstance(seq, list):
            for level in count():
                if not seq:
                    return level
                seq = list(chain.from_iterable(s for s in seq if isinstance(s, Sequence)))
                logger.info(f"LOOP")
        else:
            level = 0
            return level

    @staticmethod
    def multiply_tensors(tensors, factor=1.0, left_f=None, right_f=None):
        if isinstance(tensors, list):
            get_datahandler = DataHandler()
            pooled_output = tensors[0][1]['pooled_output']
            tensors = get_datahandler.flatten(tensors)[0]
            if left_f is None and right_f is None:
                left_f = factor
                right_f = factor
            tensors = tensors * left_f
            pooled_output = pooled_output * right_f
            pooled_output = {'pooled_output': pooled_output}
            tensors = [[tensors] + [pooled_output]]
            return tensors

    def mod_tensors(self, tensors, operation):
        if isinstance(tensors, list):
            pooled_output = tensors[0][1]['pooled_output']
            tensor = self.flatten(tensors)[0]

            if operation == "norm_tensor":
                tensor = (tensor - tensor.min()) / (tensor.max() - tensor.min())
            elif operation == "standardize_tensor":
                tensor = (tensor - tensor.mean()) / tensor.std()
            elif operation == "pool_mean":
                tensor = tensor.mean(dim=2)
            elif operation == "pool_max":
                tensor = tensor.max(dim=2).values
            elif operation == "pool_sequence":
                tensor = tensor.mean(dim=1)
            elif operation == "clamp_tensor":
                tensor = tensor.clamp(min=-10, max=10)
            elif operation == "squeeze_tensor":
                tensor = tensor.squeeze(0)

            pooled_output = {'pooled_output': pooled_output}
            tensors = [[tensor] + [pooled_output]]
            return tensors