class IntegerMaths:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { 
            "x": ("INT",{"default":0}),
            "y": ("INT",{"default":0}),
            "op": (["x+y","x-y","x*y","x//y","x%y"]),
            } }
    RETURN_TYPES = ("INT",)

    FUNCTION = "func"
    def func(self, x:int, y:int, op:str):
        if   op=="x+y":  return (x+y,)
        elif op=="x-y":  return (x-y,)
        elif op=="x*y":  return (x*y,)
        elif op=="x//y": return (x//y,)
        elif op=="x%y":  return (x%y,)

CLAZZES = [IntegerMaths]