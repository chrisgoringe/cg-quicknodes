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
        string = random.choice( to_string_list(options) ) 
        return parse_string(string)
    
CLAZZES = [ListFromList, RandomFromList, RandomFloats]