
class CombineStrings:
    FUNCTION = "func"
    CATEGORY = "quicknodes"
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"template": ("STRING", {"default":"[X] [Y]" })},
            "optional": { "x": ("STRING", {}), "y": ("STRING", {}) }
        }
    RETURN_TYPES = ("STRING",)
    def func(self, template:str, x="", y=""):
        return (template.replace("[X]",str(x)).replace("[Y]",str(y)),)
    
class Substitute:
    FUNCTION = "func"
    CATEGORY = "quicknodes"
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"string": ("STRING", {"default":"" }), "replace_": ("STRING", {"default":"" }), "with_": ("STRING", {"default":"" })}
        }
    RETURN_TYPES = ("STRING",)
    def func(self, string:str, replace_, with_):
        return (string.replace(replace_, with_),)
    
CLAZZES = [CombineStrings,Substitute]