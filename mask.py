class InvertMaskOptional:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"mask": ("MASK",),"invert": (["yes","no"],{}),}}

    CATEGORY = "quicknodes"
    RETURN_TYPES = ("MASK",)
    FUNCTION = "func"

    def func(self, mask, invert):
        return (1. - mask,) if invert=="yes" else (mask,)
    
CLAZZES = [InvertMaskOptional]