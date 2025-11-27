import torch
import math
from ui_decorator import ui_signal

import os
from PIL import Image, ImageOps
import numpy as np

from typing import Optional
from comfy_api.latest import ComfyExtension, io

import node_helpers

def load_image_as_tensor(filepath: str) -> torch.Tensor:
    image = ImageOps.exif_transpose(Image.open(filepath))
    image = np.array(image).astype(np.float32) / 255.0
    image = torch.from_numpy(image).unsqueeze(0)
    return image

class AddReferenceImage(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="AddReferenceImage",
            category="quicknodes/images",
            description="Add a reference image; if no image provided, passes conditioning unchanged",
            inputs=[
                io.Image.Input("image", optional=True),
                io.Vae.Input("vae"),
                io.Conditioning.Input("conditioning")
            ],
            outputs=[
                io.Conditioning.Output("conditioning_out"),
            ],
        )
        
    @classmethod
    def execute(cls, vae, conditioning, image=None): # type: ignore
        if image is not None:
            latent_pixels = vae.encode(image[:,:,:,:3])
            conditioning = node_helpers.conditioning_set_values(conditioning, {"reference_latents": [latent_pixels]}, append=True)
        return io.NodeOutput(conditioning)


class ImageDifference(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="ImageDifference",
            category="quicknodes/images",
            inputs=[
                io.Image.Input("image1"),
                io.Image.Input("image2"),
                io.Float.Input("multiplier", default=1.0)
            ],
            outputs=[
                io.Image.Output("image"),
                io.Float.Output("mse", is_output_list=True)
            ],
            is_output_node=True
        )
        
    @classmethod
    def execute(cls, image1:torch.Tensor, image2:torch.Tensor, multiplier:float): # type: ignore
        if image1.shape != image2.shape: 
            print(f"Both inputs must be the same batch size and image dimensions. Got {image1.shape} != {image2.shape}.")
            return io.NodeOutput(image1, [0.0,])
        d = torch.clip(torch.abs(image1-image2) * multiplier , 0.0, 1.0)
        mse = [ float(torch.nn.functional.mse_loss(image1[i], image2[i])) for i in range(image1.shape[0]) ]
        return io.NodeOutput(d, mse)   


class ImageMultiBatch(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="ImageMultiBatch",
            category="quicknodes/images",
            inputs=[
                io.Image.Input("image1", optional=True),
                io.Image.Input("image2", optional=True),
                io.Image.Input("image3", optional=True),
                io.Image.Input("image4", optional=True),
            ],
            outputs=[
                io.Image.Output("image", display_name="images"),
                io.Int.Output("frames", display_name="frames")
            ],
        )

    @classmethod
    def execute(cls, **kwargs)-> io.NodeOutput:
        images:list[torch.Tensor] = [kwargs[k] for k in kwargs if kwargs[k] is not None]
        try:
            s = torch.cat(images, dim=0) if images else None
        except Exception as e:
            print(f"Error concatenating images in ImageMultiBatch: {e}")
            s = None
        return io.NodeOutput(s, s.shape[0] if s is not None else 0) 

class LoadImagesAsBatch:
    CATEGORY = "quicknodes/images"
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder": ("STRING", {"default":""}),
                "indices": ("STRING", {"default": "-4:", "tooltip" : "python slice syntax to select images, e.g. -4: for last 4 images"}),
            }
        }

    RETURN_TYPES = ("IMAGE","INT","INT","STRING")
    RETURN_NAMES = ("image","width","height","shape")
    FUNCTION = "func"

    CATEGORY = "tools"

    def func(self, folder:str, indices:str) -> tuple[torch.Tensor,int,int,str]:
        filepaths = [ os.path.join(folder,f) for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')) ]
        filepaths.sort()
        x, y = indices.split(':')
        x = int(x) if x else None
        y = int(y) if y else None

        images = torch.cat([load_image_as_tensor(f) for f in filepaths[x:y]])
        B, H, W, C = images.shape

        return (images, W, H, f"B={B} W={W} H={H}") 


@ui_signal('display_text')
class ImageSize:
    CATEGORY = "quicknodes/images"
    @classmethod
    def INPUT_TYPES(s):
        return {"required": { "image": ("IMAGE",), } }
    RETURN_TYPES = ("IMAGE","INT","INT")
    RETURN_NAMES = ("image","w","h")
    FUNCTION = "func"

    def func(self, image:torch.Tensor):
        b, h, w, c = image.shape
        return (image,w,h,f"{w} x {h}")
    
class ImagesSize:
    CATEGORY = "quicknodes/images"
    TIP = {"tooltip":"returns the size of the first image that is not None"}
    @classmethod
    def INPUT_TYPES(s):
        return {"optional": { "i1": ("IMAGE",s.TIP), "i2": ("IMAGE",s.TIP), "i3": ("IMAGE",s.TIP), } }
    RETURN_TYPES = ("INT","INT")
    RETURN_NAMES = ("w","h")
    FUNCTION = "func"

    def func(self, i1:Optional[torch.Tensor]=None, i2:Optional[torch.Tensor]=None, i3:Optional[torch.Tensor]=None):
        for i in [i1,i2,i3]:
            if i is not None:
                b, h, w, c = i.shape
                return (w,h)
        return (0,0)
    
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
           "size": (['1024x1024 (1:1)', '1152x896 (1.286:1)', '1216x832 (1.462:1)', '1344x768 (1.75:1)', '1536x640 (2.4:1)', '1280x720 (16:9)', "1920x1080 (16:9)",
                     '512x512 (1:1)', '576x448 (1.286:1)', '608x416 (1.462:1)', '672x384 (1.75:1)', '768x320 (2.4:1)', '640x360 (16:9)', ],), 
           "orientation": (["landscape", "portrait"],)
           }  }
    
    RETURN_TYPES = ("INT","INT")
    RETURN_NAMES = ("w","h")
    FUNCTION = "func"

    def func(self, size, orientation):
        size = size.split(' ')[0]
        wh = tuple(int(x) for x in size.split("x"))
        if (orientation=="landscape"):
            return wh
        else:
            return (wh[1], wh[0])
        
class DynamicSizePicker:
    CATEGORY = "quicknodes/images"
    @classmethod
    def INPUT_TYPES(s):
       return {
           "required": { 
                "guide": ("INT", {"default":1024, "tooltip":"approximate length of side if square"}),
                "constraint": ("INT", {"default":8, "min":1, "max":1024, "tooltip":"W and h must be a multiple of this"}),
                "w": ("INT", {"default":1024}),
                "h": ("INT", {"default":1024}),
                "aspect_ratio": ("FLOAT", {"default":1.0, "min":0.1, "max":10.0, "step":0.01, "tooltip":"width / height"}),
           }
       }
    
    RETURN_TYPES = ("INT","INT")
    RETURN_NAMES = ("width","height")
    FUNCTION = "func"

    def func(self, w, h, **kwargs):
        return (w,h)
        
def resize(image, height, width):
    h,w = image.shape[1:3]
    if h==height and w==width:
        return image
    permed = torch.permute(image,(0, 3, 1, 2))
    scaled = torch.nn.functional.interpolate(permed, size=(height, width))
    return torch.permute(scaled, (0, 2, 3, 1))

class ResizeByArea:
    CATEGORY = "quicknodes/images"
    @classmethod
    def INPUT_TYPES(cls):
        return {"required":  { 
            "constraint": (["x8", "x16", "x64", "x112", "none"],),
            "image": ("IMAGE",),
            "size": ("INT", {"default":1024, "min":1, "max":10000, "tooltip":"Square root of target area in pixels"}),
            "down_only": ("BOOLEAN", {"default":False, "tooltip":"Only resize if the image is larger than the target area (will still adjust to meet constraint)"}),
        }}
    RETURN_TYPES = ("IMAGE","INT","INT",)
    RETURN_NAMES = ("image","width","height",)
    FUNCTION = "func"

    def func(self, constraint:str, image:torch.Tensor, size:int, down_only:bool=False):
        h, w = image.shape[1:3]
        scale = size / math.sqrt(h * w)

        if down_only and scale > 1.0: scale = 1.0

        c = 1 if constraint=="none" else int(constraint[1:])
        h, w = int(((h*scale + (c/2)) // c) * c), int(((w*scale + (c/2)) // c) * c)
        image = resize(image, h, w)

        return (image, w, h, )

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

    def func(self, constraint:str, image:torch.Tensor, factor:float=1.0, max_dimension:int=0, image_to_match:Optional[torch.Tensor]=None):
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
        
        return (resize(image, height, width),
                resize(image_to_match if image_to_match is not None else image, height, width),
                width, height, f"{width}x{height}") 

CLAZZES = [ ImageSize, ImagesSize, ResizeImage, SizePicker, ImageDifference, CalculateRescale, LoadImagesAsBatch, ResizeByArea, ImageMultiBatch, DynamicSizePicker, AddReferenceImage]
'''
class QuicknodesExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            ImageMultiBatch,
        ]

async def comfy_entrypoint() -> QuicknodesExtension:
    return QuicknodesExtension()'''