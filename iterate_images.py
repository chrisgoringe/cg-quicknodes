
from ui_decorator import ui_signal
import os, json, random, shutil
from PIL import Image, ImageOps
import numpy as np
import torch
from comfy.model_management import InterruptProcessingException
from typing import Optional

def load_image(filepath:str) -> tuple[torch.Tensor, str]:
        i = Image.open(filepath)
        text = i.text if hasattr(i,'text') else {} # type: ignore
        i = ImageOps.exif_transpose(i)
        image = i.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        return torch.from_numpy(image)[None,], json.dumps(text, indent=1)

def safe_move(filepath:str, target_directory:str):
    if not os.path.exists(filepath): return
    if not os.path.exists(target_directory): os.makedirs(target_directory, exist_ok=True)
    targetpath = os.path.join(target_directory, os.path.basename(filepath))
    while os.path.exists(targetpath): targetpath = os.path.splitext(targetpath)[0] + f"{random.randint(1000000,9999999)}" + os.path.splitext(targetpath)[1]
    shutil.move(filepath, targetpath)

@ui_signal(['modify_self','terminate'], output_node=False)
class IterateImages:
    FUNCTION = "func"
    MODE_TIP = '''iterate runs through each file in turn then stops. 
loop loops when it gets to the end.
replace restarts each time. 
restart_iterate restarts and switches to iterate.'''
    def __init__(self):
        self.last_was:Optional[str]         = None
        self.files_left:Optional[list[str]] = None
        self.hsh:str = ""

    @classmethod    
    def INPUT_TYPES(cls):
        return {"required":  { 
            "folder": ("STRING", {} ), 
            "extensions": ("STRING", {"default":".jpg,.png"}),
            "require_text": ("BOOLEAN", {"default":False, "tooltip":"Only pick image files which also hacve a .txt file"}),
            "text_extension": (['.txt', '.json'], {}),
            "order": (["newest_first", "oldest_first", "alphabetical", "random"], {}),
            "mode": (["iterate", "loop", "replace", "restart_iterate"], {"tooltip":cls.MODE_TIP}),
            "delete": ("BOOLEAN", {"default":False, "tooltip":"Actually moves them to subdirectory 'bin'"}),
        }}

    RETURN_TYPES = ("IMAGE","STRING","STRING","STRING","INT",)
    RETURN_NAMES = ("image","filepath","metadata",".txt","left",)
    CATEGORY = "quicknodes/images"

    def load_and_sort(self, folder, extensions, require_text, text_extension, order):
        def make_ext(s:str) -> str: return s.strip() if s.strip().startswith(".") else "."+s.strip()
        extension_list = [make_ext(s) for s in extensions.split(",")]
        def matches_extension(filename):
            split = os.path.splitext(filename)
            return len(split)>0 and split[1] in extension_list
        def has_textfile(filename):
            return os.path.exists(os.path.join(folder, os.path.splitext(filename)[0]+text_extension))
        self.files_left = [file for file in os.listdir(folder) if matches_extension(file) and (not require_text or has_textfile(file))]

        if order=="oldest_first" or order=="newest_first": key = lambda f:os.path.getmtime(os.path.join(folder, f))
        elif order=="random":                              key = lambda _:random.random()
        else:                                              key = lambda f:f
        self.files_left.sort( key=key, reverse=order=="newest_first" )


    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")
        
    def func(self, folder:str, extensions:str, require_text:bool, text_extension:str, order:str, mode:str, delete:bool):
        hsh = f"{folder}{extensions}{require_text}{text_extension}{order}"
        if (    
                self.files_left is None or 
                mode=="replace"         or 
                mode=="restart_iterate" or 
                hsh!=self.hsh           or 
                (mode=="loop" and not self.files_left)
            ):
            self.load_and_sort(folder, extensions, require_text, text_extension, order) 
            self.hsh = hsh

        if not self.files_left: raise InterruptProcessingException()

        filename = self.files_left[0]
        if mode!="replace": 
            self.files_left = self.files_left[1:]

        filepath        = os.path.join(folder, filename)
        image, metadata = load_image(filepath)
        textpath        = os.path.splitext(filepath)[0] + text_extension

        if os.path.exists(textpath):
            with open(textpath,'r',encoding='utf8') as fh: 
                if text_extension==".json":
                    texts = json.load(fh)
                    text = random.choice(texts)
                else:
                    text = "\n".join(fh.readlines())
        else:
            text = ""

        if delete: 
            bin_dir = os.path.join(os.path.dirname(filepath), 'bin')
            safe_move(filepath, bin_dir)
            safe_move(textpath, bin_dir)

        widget_changes    = [("mode","iterate"),] if mode=="restart_iterate" else []
        terminate_command = "autoqueueoff" if (mode=="iterate" and not self.files_left) else "no"

        return (image, filepath, metadata, text, len(self.files_left), widget_changes, terminate_command)

CLAZZES = [IterateImages,]