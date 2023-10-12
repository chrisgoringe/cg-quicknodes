class CommonSizes:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "size": (read_config('sizes'), {}) } }
    RETURN_TYPES = ("INT","INT")
    RETURN_NAMES = ("width","height")
    FUNCTION = "func"
    def func(self,size:str):
        x, y = [int(v) for v in size.split('x')]
        return (x,y)
    
CLAZZES = [CommonSizes]