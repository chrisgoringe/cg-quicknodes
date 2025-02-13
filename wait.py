import time

class WaitABit:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "seconds": ("INT", {"default":0}), "image": ("IMAGE",{}) }}
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "func"
    def func(self,seconds, image):
        time.sleep(seconds)
        return (image,)
    
CLAZZES = [WaitABit,]