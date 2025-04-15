import random

def parse_string(string):
    try: f = float(string)
    except: f = 0
    try: i = int(string)
    except: i = 0
    try: w, h = (int(x.strip()) for x in string.split('x'))
    except: w = h = 0
    return (string, f, i, w, h)

def to_string_list(options):
    lines = ( o.split("#")[0].strip() for o in options.split("\n") if o )
    return list( line for line in lines if line )

class RandomInt:
    RETURN_TYPES = ("INT", "STRING")
    CATEGORY = "quicknodes/random"
    FUNCTION = "func"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { 
            "seed": ("INT", {"default":0, "min":0, "max":1e9}),
            "_min": ("INT", {"default":1000000, "min": -1e9, "max":1e9}),
            "_max": ("INT", {"default":9999999, "min": -1e9, "max":1e9})
        }}
    
    def func(self, seed, _min, _max):
        random.seed(seed)
        i = random.randint(_min, _max)
        return (i, str(i))

class RandomFloats:
    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT")
    CATEGORY = "quicknodes/random"
    FUNCTION = "func"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { 
            "seed": ("INT", {"default":0, "min":0, "max":1e9}),
            "_min": ("FLOAT", {"default":0, "min": -1000, "max":1000}),
            "_max": ("FLOAT", {"default":0, "min": -1000, "max":1000}),
            "_round": ("INT", {"default":2, "min": 0, "max":10})
        }}
    
    def func(self, seed, _min, _max, _round):
        random.seed(seed)
        return tuple(round(_min + (_max-_min)*random.random(), _round) for _ in range(3))

class Base:
    RETURN_TYPES = ("STRING", "FLOAT", "INT", "INT", "INT")
    RETURN_NAMES = ("string","float", "int", "w", "h")
    CATEGORY = "quicknodes"
    FUNCTION = "func"
    
class ListFromList(Base):
    OUTPUT_IS_LIST = (True,True,True,True,True)
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "options": ("STRING", {"default":"", "multiline": True})} }
    
    def func(self, options):
        options = to_string_list(options)
        results = ([],[],[],[],[])
        for parsed in (parse_string(o) for o in options):
            for i in range(5): results[i].append(parsed[i])
        return results

class RandomFromList(Base):
    CATEGORY = "quicknodes/random"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "seed": ("INT", {"default":0, "min":-1e9, "max":1e9}),
                               "options": ("STRING", {"default":"", "multiline": True})} }

    def func(self,seed,options):
        random.seed(seed)
        choices = to_string_list(options)
        string = random.choice( choices ) if len(choices) else ""
        return parse_string(string)
    
class AppendRandomFromList:
    CATEGORY = "quicknodes/random"
    FUNCTION = "func"
    @classmethod    
    def INPUT_TYPES(s):
        return {"required": {  
                                "seed": ("INT", {"default":0, "min":-1e9, "max":1e9}),
                                "seed_offset": ("INT", {"default":0, "min":-1e9, "max":1e9}),
                                "divider": ("STRING", {"default":", "}),
                                "options": ("STRING", {"default":"", "multiline": True})
                            },
                "optional": {   
                                "in_string": ("STRING", {"default":"", "forceInput":True} ),
                            }
                }
    RETURN_TYPES = ("STRING",)

    def func(self,seed,seed_offset,divider,options,in_string=None):
        random.seed(seed+seed_offset)
        choices = to_string_list(options)
        string = random.choice( choices )  if len(choices) else ""
        if in_string: string = in_string + ((divider + string) if string else "")
        return (string,)   
    
CLAZZES = [ListFromList, RandomFromList, RandomFloats, AppendRandomFromList, RandomInt]