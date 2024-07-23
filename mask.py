import torch

class InvertMaskOptional:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"mask": ("MASK",),"invert": (["yes","no"],{}),}}

    CATEGORY = "quicknodes"
    RETURN_TYPES = ("MASK",)
    FUNCTION = "func"

    def func(self, mask, invert):
        return (1. - mask,) if invert=="yes" else (mask,)
    
    
class MaskToBlack:
    CATEGORY = "quicknodes"
    @classmethod
    def INPUT_TYPES(s):
       return {"required": { "image": ("IMAGE",), "mask": ("MASK",), "invert": (["no", "yes"], )} }
    RETURN_TYPES = ( "IMAGE", )
    FUNCTION = "func"

    def func(self, image:torch.Tensor, mask:torch.Tensor, invert:str):
        if len(mask.shape)==2: mask.unsqueeze_(0)
        invert = (invert=="yes")
        out_images = []
        for img, msk in zip(image, mask):
            if invert: msk = 1.0 - msk
            out_images.append( torch.where(msk.unsqueeze(-1).expand((-1,-1,3))>0.5, torch.zeros_like(img), img) )
        return (torch.stack( out_images, dim=0 ), )
    
CLAZZES = [InvertMaskOptional, MaskToBlack, ]