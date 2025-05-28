import torch
import math
from ui_decorator import ui_signal

@ui_signal('display_text')
class ImageDifference:
    CATEGORY = "quicknodes/images"
    @classmethod
    def INPUT_TYPES(s):
        return {"required": { 
           "image1": ("IMAGE",), 
           "image2": ("IMAGE",), 
           "multiplier": ("FLOAT", {"default":1.0, "min":0}),
        }  }
    RETURN_TYPES = ("IMAGE", "FLOAT")
    RETURN_NAMES = ("difference", "mse")
    FUNCTION = "func"

    def func(self, image1:torch.Tensor, image2:torch.Tensor, multiplier:float):
        b1, h1, w1, _ = image1.shape
        b2, h2, w2, _ = image2.shape
        if (h1!=h2 or w1!=w2 or b1!=1 or b2!=1):
            return (image1, 0.0, "need two single images of same size")
        d = torch.abs(image1-image2) * multiplier
        mse = float(torch.nn.functional.mse_loss(image1, image2))
        return (d, mse, f"{mse:>10.8f}")   

@ui_signal('display_text')
class ImageSize:
    CATEGORY = "quicknodes/images"
    @classmethod
    def INPUT_TYPES(s):
        return {"required": { "image": ("IMAGE",), } }
    RETURN_TYPES = ("INT","INT")
    RETURN_NAMES = ("w","h")
    FUNCTION = "func"

    def func(self, image:torch.Tensor):
        b, h, w, c = image.shape
        return (w,h,f"{w} x {h}")
    
class CalculateRescale:
    CATEGORY = "quicknodes/images"
    @classmethod
    def INPUT_TYPES(s):
        return {"required": { 
            "w": ("INT",{"default":1024, "min":1, "max":10000}), 
            "h": ("INT",{"default":1024, "min":1, "max":10000}),
            "guide": ("INT",{"default":1024, "min":1, "max":10000, "tooltip":"Desired image square dimension"}),
        } }    
    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "func"

    def func(self, w:int, h:int, guide:int):
        return (math.sqrt(guide*guide/(w*h)),)
    
class SizePicker:
    CATEGORY = "quicknodes/images"
    @classmethod
    def INPUT_TYPES(s):
       return {"required": { 
           "size": (['1024x1024', '1152x896', '1216x832', '1344x768', '1536x640', '1600x900', ],), 
           "orientation": (["landscape", "portrait"],)
           }  }
    
    RETURN_TYPES = ("INT","INT")
    RETURN_NAMES = ("w","h")
    FUNCTION = "func"

    def func(self, size, orientation):
        wh = tuple(int(x) for x in size.split("x"))
        if (orientation=="landscape"):
            return wh
        else:
            return (wh[1], wh[0])
    

class ResizeImage:
    CATEGORY = "quicknodes/images"
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

CLAZZES = [ ImageSize, ResizeImage, SizePicker, ImageDifference, CalculateRescale]