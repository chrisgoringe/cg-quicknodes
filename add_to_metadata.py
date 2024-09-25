from nodes import LoadImage
import folder_paths
from PIL import Image

class AddToMetadata:
    CATEGORY = "quicknodes/metadata"
    @classmethod
    def INPUT_TYPES(s):
        return {"required":  { 
            "image": ("IMAGE", {}),
            "label": ("STRING",{"default":"prompt"}),
            "value": ("STRING",{"default":""}),
        },"hidden" : {
            "extra_pnginfo": "EXTRA_PNGINFO",
        }}
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "func"

    def func(self, image, label, value, extra_pnginfo):
        extra_pnginfo[label] = value
        return (image,)
    
class LoadImageWithMetadata(LoadImage):
    CATEGORY = "quicknodes/metadata"
    FUNCTION = "func"
    RETURN_TYPES = ["IMAGE", "MASK", "JSON", "STRING",   ]
    RETURN_NAMES = ["image", "mask", "json", "filepath", ]

    def func(self, **kwargs):
        filepath = folder_paths.get_annotated_filepath(kwargs['image'])
        try:
            with Image.open(filepath) as img: text = img.text
        except:
            text = {}
        return self.load_image(**kwargs) + (text,filepath,)

CLAZZES = [AddToMetadata, LoadImageWithMetadata]