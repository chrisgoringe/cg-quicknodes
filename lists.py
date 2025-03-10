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


CLAZZES = [IntList,FloatList, Permutations]