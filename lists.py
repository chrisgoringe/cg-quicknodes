import math

class List:
    CATEGORY = "quicknodes/lists"
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "func"

    def func(self, start, step, count=0, end=0):
        count = count or (1+int((end-start)/step) if step else 1)
        lst = [ start + i*step for i in range(count) ]
        return (lst,)
    
class IntList(List):
    @classmethod    
    def INPUT_TYPES(s): return { 
        "required":  { 
            "start": ("INT",{"default":0, "min":-1e9, "max":1e9}), 
            "step" : ("INT",{"default":1, "min":-1e9, "max":1e9}),
        },
        "optional": {
            "count" :  ("INT",{"default":0, "min":0, "max":1e9, "toolip":"if non-zero, count is used instead of end"}),
            "end"   :  ("INT",{"default":10, "min":-1e9, "max":1e9, "toolip":"end is included"}),
        } }
    RETURN_TYPES = ("INT",)

class FloatList(List):
    @classmethod    
    def INPUT_TYPES(s): return { 
        "required":  { 
            "start": ("FLOAT",{"default":0,"min":-20000,"max":20000}), 
            "step" : ("FLOAT",{"default":0.1}),
        },
        "optional": {
            "count" :  ("INT",{"default":0, "min":0, "max":1e9, "toolip":"if non-zero, count is used instead of end"}),    
            "end"   :  ("FLOAT",{"default":1,"min":-20000,"max":20000}),
        } }
    RETURN_TYPES = ("FLOAT",)

class Permutations:
    CATEGORY = "quicknodes/lists"
    OUTPUT_IS_LIST = (True,True,True,)
    FUNCTION = "func"
    RETURN_TYPES = ("FLOAT","FLOAT","FLOAT")
    @classmethod    
    def INPUT_TYPES(s): return { "required":  { 
        "start" : ("FLOAT",{"default":1, "step":0.05, "min":-2, "max":2}), 
        "step"  : ("FLOAT",{"default":0.1, "step":0.05,"min":0,"max":2}),
        "steps" : ("INT",{"default":1, "min":1, "max":10}),
        "outs"  : ("INT",{"default":3, "min":1, "max":3}),
        } }
    
    def func(self, start, step, steps, outs):
        n = int(math.pow(steps, outs))
        return (
            [start+step*(i % steps)          for i in range(n)],
            [start+step*((i//steps) % steps) for i in range(n)],
            [start+step*(i//(steps*steps))   for i in range(n)],
        )
    
class PermuteInts:
    CATEGORY = "quicknodes/lists"
    OUTPUT_IS_LIST = (True,True,True,True)
    FUNCTION = "func"
    RETURN_TYPES = ("INT","INT","INT","INT")
    @classmethod    
    def INPUT_TYPES(s): return { "required":  { 
        "max1" : ("INT",{"default":0, "min":0, "max":10}), 
        "max2" : ("INT",{"default":0, "min":0, "max":10}),
        "max3" : ("INT",{"default":0, "min":0, "max":10}),
        "max4" : ("INT",{"default":0, "min":0, "max":10}),
    } }
    
    def func(self, max1, max2, max3, max4):
        outs = ([],[],[],[])
        for i in range(max1+1):
            for j in range(max2+1):
                for k in range(max3+1):
                    for l in range(max4+1):
                        outs[0].append(i)
                        outs[1].append(j)
                        outs[2].append(k)
                        outs[3].append(l)

        return outs
    
class Permutations:
    CATEGORY = "quicknodes/lists"
    OUTPUT_IS_LIST = (True,True,True,)
    FUNCTION = "func"
    RETURN_TYPES = ("FLOAT","FLOAT","FLOAT")
    @classmethod    
    def INPUT_TYPES(s): return { "required":  { 
        "start" : ("FLOAT",{"default":0.0, "step":0.1}), 
        "step" : ("FLOAT",{"default":0.0, "step":0.1}),
        "steps" : ("INT",{"default":0, "min":0, "max":100}),
        "outs" :  ("INT",{"default":3, "min":1, "max":3}),
    } }
    
    def func(self, start, step, steps, outs):
        n = int(math.pow(steps, outs))
        return (
            [start+step*(i % steps)          for i in range(n)],
            [start+step*((i//steps) % steps) for i in range(n)],
            [start+step*(i//(steps*steps))   for i in range(n)],
        )    
    
def to_string_list(options):
    lines = ( o.split("#")[0].strip() for o in options.split("\n") if o )
    return list( line for line in lines if line )

class PickFromList:
    CATEGORY = "quicknodes/random"
    FUNCTION = "func"
    RETURN_TYPES = ("STRING",)
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { 
            "options": ("STRING", {"default":"", "multiline": True, "tooltip":"one entry per line. # comments"}),
            "entry": ("INT", {"default":0, "min":0, "max":1e9, "tooltip":"zero index, wraps"}),
        } }

    def func(self,options,entry):
        choices = to_string_list(options)
        return (choices[entry % len(choices)],) if choices else ("",)
    
CLAZZES = [IntList,FloatList, Permutations, PickFromList, PermuteInts]