from datetime import date

class ToString:
    FUNCTION = "func"
    CATEGORY = "quicknodes"
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "optional": { 
                "format_": ("STRING", {"default":"", "tooltip":"Optional python formnat string. Overrides float_dp."}),
                "int_": ("INT", {"forceInput":True, "tooltip":"Optional. Ignored if float_ provided."}), 
                "float_": ("FLOAT", {"forceInput":True, "tooltip":"Optional. Takes precedence over int_"}), 
                "float_dp": ("INT", {"default":2, "tooltip":"If no format string, and using float_, round to this number of decimal places."}) }
        }
    RETURN_TYPES = ("STRING",)

    def wrap_format(self,f):
        if not f.startswith('{'): f = '{' + f
        if not f.endswith('}'): f = f + '}'
        return f
    
    def func(self, format_="", int_=None, float_=None, float_dp=2):
        if float_ is not None:
            if format_:  return (self.wrap_format(format_.strip()).format(float_),)
            if float_dp: return (f"{round(float_, float_dp)}",)
            else:        return (f"{float_}",)
        elif int_ is not None:       
            if format_:  return (self.wrap_format(format_.strip()).format(int_),)
            else:        return (f"{int_}",)
        else:            return ("",)
  
class ToInt:
    FUNCTION = "func"
    CATEGORY = "quicknodes"
    @classmethod
    def INPUT_TYPES(s):
        return { "required": { "string" : ("STRING", {"forceInput":True}) }, }
    RETURN_TYPES = ("INT",)
    def func(self, string):
        try:
            return (round(float(string.strip())),)   
        except:
            return (0,)
        
class ToFloat:
    FUNCTION = "func"
    CATEGORY = "quicknodes"
    @classmethod
    def INPUT_TYPES(s):
        return { "required": { "string" : ("STRING", {"forceInput":True}) }, }
    RETURN_TYPES = ("FLOAT",)
    def func(self, string):
        try:
            return (float(string.strip()),)   
        except:
            return (0.0,)   

class CombineStrings:
    FUNCTION = "func"
    CATEGORY = "quicknodes"
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"template": ("STRING", {"default":"[X] [Y]", "tooltip":"use [D] for date" })},
            "optional": { "x": ("STRING", {}), "y": ("STRING", {}) }
        }
    RETURN_TYPES = ("STRING","STRING","STRING",)
    RETURN_NAMES = ("merged","x","y")
    def func(self, template:str, x="", y=""):
        r = template.replace("[X]",str(x)).replace("[Y]",str(y)).replace('[D]',date.today().isoformat())
        return (r,x,y,)
    
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
    
CLAZZES = [CombineStrings,Substitute, ToString, ToInt, ToFloat]