from comfy_api.latest import io

import random
from typing import Optional

def parse_string(string):
    try: f = float(string)
    except: f = 0
    try: i = int(string)
    except: i = 0
    try: w, h = (int(x.strip()) for x in string.split('x'))
    except: w = h = 0
    return (string, f, i, w, h)

def to_string_list(options:str, allow_blanks=False, remove_space=True, might_be_file=True) -> list[str]:
    lines = options.split("\n")

    if len(lines)==1 and might_be_file:
        try:
            with open(lines[0], 'r') as fh: lines = fh.readlines()
        except Exception as e:
            print(f"{e} reading {lines[0]}")

    lines = [ line.split('#')[0] for line in lines if not line.startswith('#') ]

    if remove_space:     lines = [line.strip() for line in lines]
    if not allow_blanks: lines = [line for line in lines if line]
    return lines

class RandomInt:
    RETURN_TYPES = ("INT", "STRING")
    CATEGORY = "quicknodes/random"
    FUNCTION = "func"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { 
            "_min": ("INT", {"default":1000000, "min": -1e9, "max":1e9}),
            "_max": ("INT", {"default":9999999, "min": -1e9, "max":1e9})
        }}
    
    def func(self, _min, _max, **kwargs):
        i = random.randint(_min, _max)
        return (i, str(i))
    
    @classmethod    
    def IS_CHANGED(cls, **kwargs):
        return random.random()

class RandomFloats:
    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT")
    CATEGORY = "quicknodes/random"
    FUNCTION = "func"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { 
            "_min": ("FLOAT", {"default":0, "min": -1000, "max":1000}),
            "_max": ("FLOAT", {"default":0, "min": -1000, "max":1000}),
            "_round": ("INT", {"default":2, "min": 0, "max":10})
        }}
    
    def func(self, _min, _max, _round, **kwargs):
        return tuple(round(_min + (_max-_min)*random.random(), _round) for _ in range(3))
    
    @classmethod    
    def IS_CHANGED(cls, **kwargs):
        return random.random()

class Base:
    RETURN_TYPES = ("STRING", "FLOAT", "INT", "INT", "INT")
    RETURN_NAMES = ("string","float", "int", "w", "h")
    CATEGORY = "quicknodes"
    FUNCTION = "func"

    @classmethod    
    def IS_CHANGED(cls, **kwargs):
        return random.random()
    
class ListFromList(Base):
    OUTPUT_IS_LIST = (True,True,True,True,True)
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "options_or_filepath": ("STRING", {"default":"", "multiline": True})} }
    
    def func(self, options_or_filepath):
        entries = to_string_list(options_or_filepath)
        results = ([],[],[],[],[])
        for parsed in (parse_string(o) for o in entries):
            for i in range(5): results[i].append(parsed[i])
        return results

class RandomFromList(Base):
    CATEGORY = "quicknodes/random"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "options_or_filepath": ("STRING", {"default":"", "multiline": True})} }

    def func(self,options_or_filepath, **kwargs):
        choices = to_string_list(options_or_filepath)
        string = random.choice( choices ) if len(choices) else ""
        return parse_string(string)

class AppendString:
    CATEGORY = "quicknodes/strings"
    FUNCTION = "func"

    @classmethod    
    def INPUT_TYPES(s):
        return {"required": {  
                                "addition": ("STRING", {"multiline":True, "default":""}),
                            },
                "optional": {   
                                "in_string": ("STRING", {"default":"", "forceInput":True} ),
                            }
                }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("combined",)

    def func(self,addition,in_string=None):
        return ( (in_string or "") + addition,  )


class AppendRandomFromList(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id         = "AppendRandomFromList",
            category        = "quicknodes/random",
            inputs          = [ 
                io.String.Input('divider', default=" "),
                io.String.Input('in_string', default=""),
                io.String.Input("options_or_filepath", default="", multiline=True, tooltip="If only one line, will try to treat it as a filepath"),
                io.Int.Input('n', default=1, min=0, tooltip="minimum number of entries to append"),
                io.Int.Input('m', default=1, min=0, tooltip="maximum number of entries to append"),
                io.Boolean.Input('allow_blanks', default=False, tooltip="if false, blank lines are excluded"),
                io.Boolean.Input('remove_space', default=True, tooltip="remove whitespace from ends")
             ],
            outputs         = [ 
                io.String.Output('combined', display_name='combined'),
                io.String.Output('added', display_name='addition')
             ],
        )

    @classmethod
    def fingerprint_inputs(cls, **kwargs):
        return random.random()

    @classmethod
    def execute(  # type: ignore
        cls, 
        divider:str, 
        options_or_filepath:str, 
        n:int=1, 
        m:int=1, 
        in_string:Optional[str]=None, 
        allow_blanks:bool=False, 
        remove_space:bool=True
    ):
        choices = to_string_list(options_or_filepath, allow_blanks=allow_blanks, remove_space=remove_space)
        if m<n: m=n
        x = random.randint(n,m)

        addition_list:list[str] = random.choices( choices, k=x ) if (len(choices) and x) else []
        addition = divider.join(addition_list) if addition_list else ""

        outstring = (in_string or "") + (addition or "") 

        return io.NodeOutput(outstring, addition)   
    
CLAZZES = [ListFromList, RandomFromList, RandomFloats, AppendRandomFromList, RandomInt, AppendString]