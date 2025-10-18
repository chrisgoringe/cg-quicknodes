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
    
    
class LoadTextfile:
    CATEGORY = "quicknodes/images"

    RETURN_TYPES = ("STRING",)
    FUNCTION = "func"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "filepath": ("STRING", {"default": "output", "tooltip": "The filepath, extension will be changed."}),
                "remove": ("BOOLEAN", {"default": False, "tooltip": "Remove the file after reading."}),
            }
        }

    def func(self, filepath, remove ):
        filepath = os.path.splitext(filepath)[0]+".txt"
        with open(filepath, 'r', encoding="utf-8") as fh: s = fh.read()
        if remove: os.remove(filepath)
        return (s.strip(),)
    
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
                "filepath": ("STRING", {"default": "output", "tooltip": "The filepath, extension will be changed."}),
            },
            "optional": {  
                "ext": ("STRING", {"default": ".txt", "tooltip": "The file extension to use."}),
            }
        }

    def func(self, text, filepath, ext=".txt"):
        filepath = os.path.splitext(filepath)[0]+ext
        if not os.path.exists(os.path.split(filepath)[0]): os.makedirs(os.path.split(filepath)[0], exist_ok=True)
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
    
CLAZZES = [SaveImageExplicitPath, SaveFilename, SaveTextfile, LoadTextfile]


