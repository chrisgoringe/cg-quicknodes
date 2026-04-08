from comfy_api.latest import io
from pathlib import Path
import random, os
import numpy as np
from PIL import Image
import torch
from typing import Optional

class SaveImageInFolder(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SaveImageInFolder",
            display_name="Save Image in Folder",
            category="quicknodes/images",
            inputs  = [
                io.Image.Input("image"),
                io.String.Input("folder", tooltip="Full path of folder (will be created if required)"),
                io.String.Input("filename", optional=True, tooltip="if not provided, a random name will be generated. If provided, will be changed if needed to avoid clashes."),
                io.String.Input("text", optional=True, force_input=True, tooltip="Optional text to save in .txt"),
            ],
            outputs = [],
            is_output_node=True,
        )
    
    @classmethod
    def save_path(cls, folder:str, offered_filename:str, n:int, multiple:bool) -> Path:
        filename:Path = Path(Path(offered_filename).stem + ".png") if offered_filename else Path(f"{random.randint(1000000,9999999)}.png") 
        filename = Path(filename.stem + f"_{n}" + ".png") if multiple else filename
        filepath = Path(folder) / filename
        idx = 0
        while filepath.exists(): 
            idx += 1
            filepath = Path(folder) / (filename.stem + f"-{idx:0>6}" + ".png")
        return filepath        

    @classmethod
    def execute(cls, image:torch.Tensor|list[torch.Tensor], folder:str, filename:Optional[str]=None, text:Optional[str]=None) -> io.NodeOutput: # type: ignore
        if not os.path.exists(folder): 
            os.makedirs(folder, exist_ok=True)
            print(f"Created {folder}")

        for n,i in enumerate(image):
            image_path = cls.save_path(folder, filename or "", n, (len(image)>1))
            i = 255. * i.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            img.save(image_path)
            print(f"Saved {image_path}")
            if text:
                text_path = image_path.parent / Path(image_path.stem + ".txt")
                with open(text_path, 'w', encoding="utf-8") as fh: print(text, file=fh)
                print(f"Saved {text_path}", flush=True)
            
        return io.NodeOutput()  
    
CLAZZES = [SaveImageInFolder]