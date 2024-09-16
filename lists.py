class List:
    CATEGORY = "quicknodes/lists"
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "func"

    def func(self, start, step, end): 
        n = start
        lst = [n,]
        while (n+step<=end and step>0) or (n+step>=end and step<0):
            n += step
            lst.append(n)
        return (lst,)
    
class IntList(List):
    @classmethod    
    def INPUT_TYPES(s): return { "required":  { 
        "start": ("INT",{"default":0}), 
        "step" : ("INT",{"default":1}),
        "end" :  ("INT",{"default":10}),
        } }
    RETURN_TYPES = ("INT",)

class FloatList(List):
    @classmethod    
    def INPUT_TYPES(s): return { "required":  { 
        "start": ("Float",{"default":0}), 
        "step" : ("Float",{"default":0.1}),
        "end" :  ("Float",{"default":1}),
        } }
    RETURN_TYPES = ("FLOAT",)

CLAZZES = [IntList,FloatList]