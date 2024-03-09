import random

class StringSplit:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "split": ("STRING",{"default":""}), "fraction_top": ("FLOAT",{"default":0.5})},
                  "optional": { "common": ("STRING",{"default":""}), "seed": ("INT",{"default":0}) }
                }
    RETURN_TYPES = ("STRING","STRING",)
    RETURN_NAMES = ("string","string",)
    FUNCTION = "func"

    def IS_CHANGED(self,**kwargs):
        return float("NaN")

    def func(self, split:str, fraction_top, seed:int=0, common:str=""):
        if seed: random.seed(seed)
        splitter = lambda a : list(x.strip() for x in a.split(',') if x)
        a = splitter(common)
        b = splitter(common)
        bits = splitter(split)
        for x in bits:
            if random.random()<fraction_top: a.append(x)
            else: b.append(x)
        random.shuffle(a)
        random.shuffle(b)
        return (','.join(a), ','.join(b),)




CLAZZES = [StringSplit]