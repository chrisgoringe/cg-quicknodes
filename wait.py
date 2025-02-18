import time
from comfy.model_management import throw_exception_if_processing_interrupted

class WaitABit:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "seconds": ("INT", {"default":0}), "image": ("IMAGE",{}) }}
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "func"
    def func(self,seconds, image):
        end = time.monotonic() + seconds
        while time.monotonic < end:
            throw_exception_if_processing_interrupted()
            time.sleep(1)
        return (image,)
    
CLAZZES = [WaitABit,]