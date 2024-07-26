from folder_paths import base_path
import os, torch
from PIL import Image, ImageOps
import numpy as np
import hashlib
from nodes import SaveImage

class SaveFilename(SaveImage):
    CATEGORY = "quicknodes"

    RETURN_TYPES = ("STRING",)
    RETURN_NAME = ("filename",)
    FUNCTION = "func"

    def func(self, **kwargs):
        ret = self.save_images(**kwargs)
        ret['result'] = ( ret['ui']['images'][0]['filename'], )
        return ret

class LoadImageWithFilename():
    RETURN_TYPES = ("IMAGE", "MASK", "STRING",)
    RETURN_NAMES = ("IMAGE", "MASK", "filepath",)
    FUNCTION = "func"
    directory = os.path.join(base_path,"styles")

    @classmethod
    def INPUT_TYPES(cls):
        files = [f for f in os.listdir(cls.directory) if os.path.isfile(os.path.join(cls.directory, f))]
        return {"required": {"image": (sorted(files), {"image_upload": True})}, }

    CATEGORY = "quicknodes"

    def func(self, image):
        image_path = os.path.join(self.directory,image)
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
        return (image, mask.unsqueeze(0), image)

    @classmethod
    def IS_CHANGED(cls, image):
        image_path = os.path.join(cls.directory,image)
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(cls, image):
        return True if os.path.exists( os.path.join(cls.directory,image) ) else "Invalid image file: {}".format(image)
    
clazzes = [LoadImageWithFilename]