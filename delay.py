import time
    
class Delay:
    CATEGORY = "quicknodes"

    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { 
            "image": ("IMAGE", {}),
            "seconds": ("INT", {"default":10}),
            } }

    RETURN_TYPES = ("IMAGE", )
    RETURN_NAMES = ("image",)
    FUNCTION = "func"

    def func(self, image, seconds):
        time.sleep(seconds)
        return (image,)


CLAZZES = [Delay,]