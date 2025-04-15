class SimpleMaths:
    CATEGORY = "quicknodes"
    FUNCTION = "func"
    def func(self, x, y, op:str, dp=None):
        if   op=="add":       r = x+y
        elif op=="subtract":  r = x-y
        elif op=="multiply":  r = x*y
        elif op=="int_divide":r = x//y
        elif op=="divide":    r = x/y
        elif op=="remainder": r = x%y
        return (r,f"{round(r,dp) if dp is not None else r}",)

class SimpleIntegerMaths(SimpleMaths):
    RETURN_TYPES = ("INT","STRING",)
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { 
            "x": ("INT", {"default":0, "min":-1e9, "max":1e9}),
            "y": ("INT", {"default":0, "min":-1e9, "max":1e9}),
            "op": (["add","subtract","multiply","int_divide","remainder"],{}),
            } }

class SimpleFloatMaths(SimpleMaths):
    RETURN_TYPES = ("FLOAT","STRING",)
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { 
            "x": ("FLOAT", {"default":0, "min":-1e9, "max":1e9}),
            "y": ("FLOAT", {"default":0, "min":-1e9, "max":1e9}),
            "op": (["add","subtract","multiply","divide"],{}),
            "dp": ("INT", {"default" : 2, "tooltip":"Decimal places to round string to"})
            } }


CLAZZES = [SimpleIntegerMaths, SimpleFloatMaths]