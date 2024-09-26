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
    return list( o.strip() for o in options.split("\n") if o.strip() )

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
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "seed": ("INT", {"default":0, "min":0, "max":1e9}),
                               "options": ("STRING", {"default":"", "multiline": True})} }

    def func(self,seed,options):
        random.seed(seed)
        string = random.choice( to_string_list(options)) 
        return parse_string(string)
    
CLAZZES = [ListFromList, RandomFromList]