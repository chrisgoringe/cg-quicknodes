class SimpleIntegerMaths:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { 
            "x": ("INT",{"default":0}),
            "y": ("INT",{"default":0}),
            "op": (["add","subtract","multiply","divide","remainder"],{}),
            } }
    RETURN_TYPES = ("INT",)

    FUNCTION = "func"
    def func(self, x:int, y:int, op:str):
        if   op=="add":       return (x+y,)
        elif op=="subtract":  return (x-y,)
        elif op=="multiply":  return (x*y,)
        elif op=="divide":    return (x//y,)
        elif op=="remainder": return (x%y,)

CLAZZES = [SimpleIntegerMaths]