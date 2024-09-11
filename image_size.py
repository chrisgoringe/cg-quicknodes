import torch
from server import PromptServer
import math

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
    


class ResizeImage:
    CATEGORY = "quicknodes"
    @classmethod
    def INPUT_TYPES(s):
        return {"required":  { 
            "constraint": (["x8", "x64", "cn512", "none"],),
            "image": ("IMAGE",),
            "factor": ("FLOAT", {"default":1.0, "min":0.0, "step":0.1 }),
            "max_dimension": ("INT", {"default": 10000, "max" : 10000 }), 
        },"optional" : {
            "image_to_match": ("IMAGE",),
        }}
    RETURN_TYPES = ("IMAGE","IMAGE","INT","INT","STRING")
    RETURN_NAMES = ("image","matched_image","width","height","string")
    FUNCTION = "func"

    @classmethod
    def resize(cls, image, height, width):
        h,w = image.shape[1:3]
        if h==height and w==width:
            return image
        permed = torch.permute(image,(0, 3, 1, 2))
        scaled = torch.nn.functional.interpolate(permed, size=(height, width))
        return torch.permute(scaled, (0, 2, 3, 1))

    def func(self, constraint:str, image:torch.tensor, factor:float=1.0, max_dimension:int=0, image_to_match:torch.tensor=None):
        if image_to_match is not None:
            height, width = image_to_match.shape[1:3]
        else:
            height, width = image.shape[1:3]

        if constraint!="cn512":
            height = height * factor
            width = width * factor

            too_big_by = max(height/max_dimension, width/max_dimension)
            if too_big_by > 1.0:
                height = math.floor(height/too_big_by)
                width = math.floor(width/too_big_by)

        if constraint=="x8":
            height = ((4+height)//8) * 8
            width = ((4+width)//8) * 8
        if constraint=="x64":
            height = ((32+height)//64) * 64
            width = ((32+width)//64) * 64
        elif constraint=="cn512":
            if height >= width:
                height = (((height*512/width)+32)//64) * 64
                width = 512
            else:
                width = (((width*512/height)+32)//64) * 64
                height = 512

        height = int(height)
        width = int(width)
        
        return (self.resize(image, height, width),
                self.resize(image_to_match if image_to_match is not None else image, height, width),
                width, height, f"{width}x{height}") 

CLAZZES = [ ImageSize, ResizeImage]