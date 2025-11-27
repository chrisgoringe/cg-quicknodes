from datetime import date
import re, os, json
from comfy.comfy_types.node_typing import IO

class ToString:
    FUNCTION = "func"
    CATEGORY = "quicknodes/strings"
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "optional": { 
                "format_": ("STRING", {"default":"", "tooltip":"Optional python formnat string. Overrides float_dp."}),
                "int_": ("INT", {"forceInput":True, "tooltip":"Optional. Ignored if float_ provided."}), 
                "float_": ("FLOAT", {"forceInput":True, "tooltip":"Optional. Takes precedence over int_"}), 
                "float_dp": ("INT", {"default":2, "tooltip":"If no format string, and using float_, round to this number of decimal places."}),
                "string_": ("STRING", {"default":""}),
                "default": ("STRING", {"default":""})}
        }
    RETURN_TYPES = ("STRING",)

    def wrap_format(self,f):
        if not f.startswith('{'): f = '{' + f
        if not f.endswith('}'): f = f + '}'
        return f
    
    def func(self, format_="", int_=None, float_=None, float_dp=2, string_="", default=""):
        if float_ is not None:
            if format_:  return (self.wrap_format(format_.strip()).format(float_),)
            else:        return (f"{round(float_, float_dp)}",)
        elif int_ is not None:       
            if format_:  return (self.wrap_format(format_.strip()).format(int_),)
            else:        return (f"{int_}",)
        elif string_:    return (string_,)
        else:            return (default,)
  
class ToInt:
    FUNCTION = "func"
    CATEGORY = "quicknodes/strings"
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
    CATEGORY = "quicknodes/strings"
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
    CATEGORY = "quicknodes/strings"
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"template": ("STRING", {"default":"[X]_[Y]_[Z]", "tooltip":"use [D] for date" })},
            "optional": { "x": (IO.ANY, {}), "y": (IO.ANY, {}), "z": (IO.ANY, {}) }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("merged",)
    def func(self, template:str, x="", y="", z=""):
        r = template.replace("[X]",str(x)).replace("[Y]",str(y)).replace("[Z]",str(z)).replace('[D]',date.today().isoformat())
        return (r,)
    
class Substitute:
    FUNCTION = "func"
    CATEGORY = "quicknodes/strings"
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string": ("STRING", {"default":"" }), 
                "replace_": ("STRING", {"default":"" }), 
                "with_": ("STRING", {"default":"" }),
                "re_": ("BOOLEAN", {"default":False}),
            }
        }
    RETURN_TYPES = ("STRING",)
    def func(self, string:str, replace_, with_, re_=False):
        if re_:
            return (re.sub(replace_, with_, string),)
        else:
            return (string.replace(replace_, with_),)
        
class Split:
    FUNCTION = "func"
    CATEGORY = "quicknodes/strings"
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string": ("STRING", {"default":"" }), 
                "action": (["split","splitext",], {}),
            }
        }
    RETURN_TYPES = ("STRING","STRING",)
    
    def func(self, string, action):
        return getattr(os.path, action)(string)
    
class Common:
    FUNCTION = "func"
    CATEGORY = "quicknodes/strings"
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string1": ("STRING", {"default":"" }), 
                "string2": ("STRING", {"default":"" }), 
                "action": (["commonpath","commonprefix",], {}),
            }
        }
    RETURN_TYPES = ("STRING",)
    
    def func(self, string1, string2, action):
        try:
            return (getattr(os.path, action)([string1,string2]),)
        except ValueError:
            return ("",)
        
def decode_nested_json(json_):
    if not json_: return {}
    def ld(s):
        try: return json.loads(str(s))
        except json.decoder.JSONDecodeError: return s
        except: pass 
    return { k:ld(json_[k]) for k in json_ } if isinstance(json_,dict) else json_
        
class ExtractFromJson:
    CATEGORY = "quicknodes/strings"
    @classmethod    
    def INPUT_TYPES(s):
        return {"required" : { "json_" : ("JSON", {}), "key" : ("STRING", {"default":"prompt"})}}
    RETURN_TYPES = ("STRING",)
    FUNCTION = "func"

    def func(self, json_, key):
        if isinstance(json_,str): json_ = json.loads(json_)
        return (decode_nested_json(json_).get(key,""),)

    
CLAZZES = [CombineStrings,Substitute, ToString, ToInt, ToFloat, Split, Common, ExtractFromJson]