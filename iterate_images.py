
from ui_decorator import ui_signal
import os, json, random
from PIL import Image, ImageOps
import numpy as np
import torch
from comfy.model_management import InterruptProcessingException
from typing import Optional
from pathlib import Path

def load_image(filepath:str|Path) -> tuple[torch.Tensor, str]:
        i = Image.open(filepath)
        text = i.text if hasattr(i,'text') else {} # type: ignore
        i = ImageOps.exif_transpose(i)
        assert i
        image = i.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        return torch.from_numpy(image)[None,], json.dumps(text, indent=1)

def safe_move(filepath:Path, target_directory:Path):
    if not filepath.exists(): return
    if not target_directory.exists(): target_directory.mkdir()
    targetpath = target_directory / filepath.name 
    while os.path.exists(targetpath): 
        targetpath = target_directory / f"{filepath.stem}{random.randint(1000000,9999999)}{filepath.suffix}"
    filepath.rename(targetpath)

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
        return {
            "required":  { 
                "folder": ("STRING", {} ), 
                "extensions": ("STRING", {"default":".jpg,.png"}),
                "require_text": ("BOOLEAN", {"default":False, "tooltip":"Only pick image files which also hacve a .txt file"}),
                "text_extension": (['.txt', '.json'], {}),
                "order": (["newest_first", "oldest_first", "alphabetical", "random"], {}),
                "mode": (["iterate", "loop", "replace", "restart_iterate"], {"tooltip":cls.MODE_TIP}),
                "delete": ("BOOLEAN", {"default":False, "tooltip":"Actually moves them to subdirectory 'bin'"}),
            }, 
            "optional" : {
                "recurse": ("BOOLEAN", {"default":False}),
                "number": ("INT", {"default":1, "min":1, "max":100}),
            }
        }

    RETURN_TYPES = ("IMAGE","STRING","STRING","STRING","INT",)
    RETURN_NAMES = ("image","filepath","metadata",".txt","left",)
    OUTPUT_IS_LIST = (True,True,True,True,False)
    CATEGORY = "quicknodes/images"

    def find_in_folder(self, folder, test, recurse) -> list[str]:
        files = [file for file in os.listdir(folder) if test(file)]
        if recurse:
            for dir in [os.path.join(folder,d) for d in os.listdir(folder) if os.path.isdir(d)]:
                files.extend( self.find_in_folder(dir, test, recurse ) )
        return files

    def load_and_sort(self, folder, extensions, require_text, text_extension, order, recurse):
        make_ext = lambda s : str(s.strip() if s.strip().startswith(".") else "."+s.strip())
        extension_list = [make_ext(s) for s in extensions.split(",")]
        matches_extension = lambda filename : bool(os.path.splitext(filename)[1].lower() in extension_list)
        has_textfile = lambda filename : os.path.exists(os.path.join(folder, os.path.splitext(filename)[0]+text_extension))
        test = lambda file : matches_extension(file) and (not require_text or has_textfile(file))

        self.files_left = self.find_in_folder( folder, test, recurse ) 

        if order=="oldest_first" or order=="newest_first": key = lambda f:os.path.getmtime(os.path.join(folder, f))
        elif order=="random":                              key = lambda _:random.random()
        else:                                              key = lambda f:f
        self.files_left.sort( key=key, reverse=order=="newest_first" )


    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")
        
    def func(self, folder:str|Path, extensions:str, require_text:bool, text_extension:str, order:str, mode:str, delete:bool, recurse:bool=False, number:int=1):
        hsh = f"{folder}{extensions}{require_text}{text_extension}{order}{recurse}"
        folder = Path(folder)
        if (    
                self.files_left is None or 
                mode=="replace"         or 
                mode=="restart_iterate" or 
                hsh!=self.hsh           or 
                (mode=="loop" and not self.files_left)
            ):
            self.load_and_sort(str(folder), extensions, require_text, text_extension, order, recurse) 
            self.hsh = hsh

        if not self.files_left: raise InterruptProcessingException()

        filenames = self.files_left[:number]
        if mode!="replace": 
            self.files_left = self.files_left[len(filenames):]

        filepaths     = [folder / filename for filename in filenames]
        img_and_metas = [load_image(filepath) for filepath in filepaths]
        textpaths     = [filepath.parent / f"{filepath.stem}{text_extension}" for filepath in filepaths]

        metadatas     = [im[1] for im in img_and_metas]
        images        = [im[0] for im in img_and_metas]

        def get_txt(textpath:Path):
            try:
                with open(textpath,'r',encoding='utf8') as fh: return fh.read()
            except:
                return ""

        texts = [get_txt(textpath) for textpath in textpaths]

        if delete: 
            for filepath, textpath in zip(filepaths, textpaths):
                bin_dir = folder / 'bin'
                safe_move(filepath, bin_dir)
                safe_move(textpath, bin_dir)

        widget_changes    = [("mode","iterate"),] if mode=="restart_iterate" else []
        terminate_command = "autoqueueoff" if (mode=="iterate" and not self.files_left) else "no"

        return (images, filepaths, metadatas, texts, len(self.files_left), widget_changes, terminate_command)

class BatchImageListWithPadding:
    @classmethod    
    def INPUT_TYPES(cls):
        return { "required":  { "images": ("IMAGE", {} ),  } }

    RETURN_TYPES   = ("IMAGE",)
    RETURN_NAMES   = ("image",)
    INPUT_IS_LIST  = True
    OUTPUT_IS_LIST = (False,)
    CATEGORY       = "quicknodes/images"
    FUNCTION       = "func"

    def func(self, images):

        X = max(i.shape[1] for i in images)
        Y = max(i.shape[2] for i in images)
        padded_images = [ torch.nn.functional.pad(i,(0,0,0,Y-i.shape[2],0,X-i.shape[1])) for i in images ]
        return ( torch.cat(padded_images), )

CLAZZES = [IterateImages,BatchImageListWithPadding]