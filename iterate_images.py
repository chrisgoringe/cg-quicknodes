
from ui_decorator import ui_signal
import os, json, random
from PIL import Image, ImageOps
import numpy as np
import torch

def load_image(filepath:str) -> torch.Tensor:
        i = Image.open(filepath)
        text = i.text if hasattr(i,'text') else {}
        i = ImageOps.exif_transpose(i)
        image = i.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        return torch.from_numpy(image)[None,], json.dumps(text, indent=1)

@ui_signal(['modify_self','terminate','display_text'])
class IterateImages:

    FUNCTION = "func"
    def __init__(self):
        self.last_was = None

    @classmethod    
    def INPUT_TYPES(s):
        return {"required":  { 
        "folder": ("STRING", {} ), 
        "extensions": ("STRING", {"default":".jpg,.png"}),
        "reset": (["no","yes","always","random"], {}),
        "delete_images": (["no","yes"], {}),
        "resend_last": (["no","yes"], {}),
        }}

    RETURN_TYPES = ("IMAGE","STRING","STRING","STRING",)
    RETURN_NAMES = ("image","filepath","metadata",".txt")
    CATEGORY = "quicknodes/images"

    def reload_maybe(self, folder, extensions, reset):
        if not hasattr(self,'files_left') or reset in ["always","yes","random"]:
            extension_list = extensions.split(",")
            def is_image_filename(filename):
                split = os.path.splitext(filename)
                return len(split)>0 and split[1] in extension_list
            self.files_left = [file for file in os.listdir(folder) if is_image_filename(file)]

    @classmethod
    def IS_CHANGED(self, **kwargs):
        return float("NaN")
        
    def func(self, folder, extensions:str, reset, delete_images, resend_last):
        self.reload_maybe(folder, extensions, reset)
        if self.files_left==[]: return (None, "", [], "terminate", f"No more files matching {extensions} in {folder}")
        if reset=="random": random.shuffle(self.files_left)

        if resend_last=="yes" and self.last_was and os.path.exists(os.path.join(folder, self.last_was)):
            filename = self.last_was
        else:
            filename = self.files_left[0] 
        self.last_was = filename
        self.files_left = [f for f in self.files_left if f!=filename]

        filepath = os.path.join(folder, filename)
        
        message = f"{filename}\n{len(self.files_left)} files remaining"

        image, metadata = load_image(filepath)

        textpath = os.path.splitext(filepath)[0] + ".txt"
        try: 
            with open(textpath,'r') as f: text = "\n".join(f.readlines())
        except:
            text = ""

        if delete_images=="yes": 
            bindir = os.path.join(os.path.split(filepath)[0], 'z')
            if not os.path.exists(bindir): os.makedirs(bindir, exist_ok=True)
            while os.path.exists(outfile := os.path.join(bindir, filename)): filename = f"{random.randint(0,9)}{filename}"
            os.rename(filepath, outfile)

        return (image, filepath, metadata, text, [("reset","no"),] if reset=="yes" else [], "no" if len(self.files_left) else "autoqueueoff", message)

CLAZZES = [IterateImages,]