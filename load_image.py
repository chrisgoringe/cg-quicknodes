from PIL import Image, ImageOps
import numpy as np
import torch
import hashlib

class FileImageLoader:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "image_path": ("STRING", {"default":""}) } }
    RETURN_TYPES = ("IMAGE","MASK",)
    RETURN_NAMES = ("image","mask",)

    FUNCTION = "func"
    def func(self,image_path):
        i = Image.open(image_path)
        i = ImageOps.exif_transpose(i)
        image = i.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        if 'A' in i.getbands():
            mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
        return (image, mask.unsqueeze(0))
    
    @classmethod
    def IS_CHANGED(s, image_path):
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, image_path):
        try:
            Image.open(image_path)
        except:
            return f"{image_path} isn't an image file"
        return True
    
CLAZZES = [FileImageLoader]