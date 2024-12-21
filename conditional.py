import torch
from comfy.model_management import InterruptProcessingException
    
class StopIfUnchanged:
    CATEGORY = "quicknodes"

    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { 
            "original": ("IMAGE", {}),
            "changed": ("IMAGE", {}),
            "active": ("BOOLEAN", {"default":True, "tooltip":"If true, the run will be terminated if the two images are identical"})
            } }

    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("original", "changed")
    FUNCTION = "func"

    def func(self, original, changed, active):
        if active and original.shape==changed.shape and torch.all(original==changed): 
            raise InterruptProcessingException()
        return (original, changed)


CLAZZES = [StopIfUnchanged,]