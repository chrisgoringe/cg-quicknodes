import torch
from server import PromptServer

class ImageSize:
    CATEGORY = "quicknodes"
    @classmethod
    def INPUT_TYPES(s):
       return {"required": { "image": ("IMAGE",), }, "hidden": { "node_id": "UNIQUE_ID" }  }
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    OUTPUT_NODE = True
    FUNCTION = "func"

    def func(self, image:torch.Tensor, node_id:int):
        b, h, w, c = image.shape
        PromptServer.instance.send_sync("cg.quicknodes.textmessage", {"id": node_id, "message":f"{w} x {h}"})
        return ()
    
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
            if invert: mask = 1.0 - mask
            out_images.append( torch.where(mask.expand((-1,-1,3)), torch.zeros_like(image), image) )
        return (torch.stack( out_images, dim=0 ), )


    
CLAZZES = [ ImageSize, MaskToBlack, ]