
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
    
CLAZZES = [CombineStrings,]