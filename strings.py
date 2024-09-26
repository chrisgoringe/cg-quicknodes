  
class ToString:
    FUNCTION = "func"
    CATEGORY = "quicknodes"
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "optional": { "int_": ("INT", {"forceInput":True}), "float_": ("FLOAT", {"forceInput":True}), "float_dp": ("INT", {"default":2}) }
        }
    RETURN_TYPES = ("STRING",)
    def func(self, int_=None, float_=None, float_dp=2):
        s = ("" if int_ is None else str(int_))
        t = ("" if float_ is None else f"{round(float_, float_dp)}")
        result = f"{s}_{t}" if s and t else f"{s}{t}"
        return (result,)   

class ToInt:
    FUNCTION = "func"
    CATEGORY = "quicknodes"
    @classmethod
    def INPUT_TYPES(s):
        return { "required": { "string" : ("STRING", {"forceInput":True}) }, }
    RETURN_TYPES = ("INT",)
    def func(self, string):
        try:
            return (int(string),)   
        except:
            return (0,)   

class CombineStrings:
    FUNCTION = "func"
    CATEGORY = "quicknodes"
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"template": ("STRING", {"default":"[X] [Y]" })},
            "optional": { "x": ("STRING", {}), "y": ("STRING", {}) }
        }
    RETURN_TYPES = ("STRING","STRING","STRING",)
    RETURN_NAMES = ("merged","x","y")
    def func(self, template:str, x="", y=""):
        return (template.replace("[X]",str(x)).replace("[Y]",str(y)),x,y,)
    
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
    
CLAZZES = [CombineStrings,Substitute, ToString, ToInt]