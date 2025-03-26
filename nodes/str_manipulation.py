from ..utils import CATEGORY, prefix

class str_str:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string_1": ("STRING", {"default": '', "forceInput": True}),
                "string_2": ("STRING", {"default": '', "forceInput": True}),
                "delimiter": ("STRING", {"default": '', "multiline": False}),
            }
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "joinstring"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.TOOLS.value

    def joinstring(self, string_1, string_2, delimiter):
        joined_string = string_1 + delimiter + string_2
        return (joined_string, )

class str_str_str_str:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string_1": ("STRING", {"default": '', "forceInput": True}),
                "string_2": ("STRING", {"default": '', "forceInput": True}),
                "string_3": ("STRING", {"default": '', "forceInput": True}),
                "string_4": ("STRING", {"default": '', "forceInput": True}),
                "delimiter": ("STRING", {"default": '', "multiline": False}),
            },
    }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "combine"
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.TOOLS.value

    def combine(self, string_1, string_2, string_3, string_4, delimiter):
        joined_string = string_1 + delimiter + string_2 + delimiter + string_3 + delimiter + string_4
        return (joined_string, )

