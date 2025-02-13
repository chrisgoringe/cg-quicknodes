from folder_paths import base_path
import os, torch, json
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngInfo
import numpy as np
import hashlib
from nodes import SaveImage
from comfy.cli_args import args
import folder_paths

class SaveFilename(SaveImage):
    CATEGORY = "quicknodes/images"

    RETURN_TYPES = ("STRING",)
    RETURN_NAME = ("filepath",)
    FUNCTION = "func"

    def func(self, **kwargs):
        ret = self.save_images(**kwargs)
        outfile = ret['ui']['images'][0]
        directory = folder_paths.get_output_directory()
        if 'subfolder' in outfile and outfile['subfolder']: directory = os.path.join(directory, outfile['subfolder'])
        ret['result'] = ( os.path.join(directory, outfile['filename']), )
        return ret
    
class SaveTextfile:
    CATEGORY = "quicknodes/images"

    RETURN_TYPES = ()
    FUNCTION = "func"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"default": ""}),
                "filepath": ("STRING", {"default": "output", "tooltip": "The filepath, extension will be changed to .txt."}),
            }
        }

    def func(self, text, filepath):
        filepath = os.path.splitext(filepath)[0]+".txt"
        with open(filepath, 'w', encoding="utf-8") as f:
            print(text, file=f)
        return ()
    
class SaveImageExplicitPath:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to save."}),
                "filepath": ("STRING", {"default": "output", "tooltip": "The full path of the file. _XXXXX will be appended."}),
                "compress": ("INT", {"default":4, "min":0, "max":9})
            },
            "hidden": {
                "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "quicknodes"

    def save_images(self, images, filepath, compress, prompt=None, extra_pnginfo=None):
        basepath, extension = os.path.splitext(filepath)
        extension = extension or ".png"
        digit = 0

        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            digit = "00000"
            while os.path.exists( f"{basepath}_{digit}{extension}" ):
                d = int(digit)
                digit = "{:0>5}".format(d+1)

            save_path = f"{basepath}_{digit}{extension}"
            img.save(save_path, pnginfo=metadata, compress_level=compress)


        return ()
    
'''
class LoadImageWithFilename():
    RETURN_TYPES = ("IMAGE", "MASK", "STRING",)
    RETURN_NAMES = ("IMAGE", "MASK", "filepath",)
    FUNCTION = "func"
    directory = os.path.join(base_path,"styles")

    @classmethod
    def INPUT_TYPES(cls):
        files = [f for f in os.listdir(cls.directory) if os.path.isfile(os.path.join(cls.directory, f))]
        return {"required": {"image": (sorted(files), {"image_upload": True})}, }

    CATEGORY = "quicknodes/images"

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
    '''
CLAZZES = [SaveImageExplicitPath, SaveFilename, SaveTextfile]
#LoadImageWithFilename, 