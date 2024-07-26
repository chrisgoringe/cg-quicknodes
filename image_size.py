import torch
from server import PromptServer

class ImageSize:
    CATEGORY = "quicknodes"
    @classmethod
    def INPUT_TYPES(s):
       return {"required": { "image": ("IMAGE",), }, "hidden": { "node_id": "UNIQUE_ID" }  }
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    OUTPUT_NODE = True
    FUNCTION = "func"

    def func(self, image:torch.Tensor, node_id:int):
        b, h, w, c = image.shape
        PromptServer.instance.send_sync("cg.quicknodes.textmessage", {"id": node_id, "message":f"{w} x {h}"})
        return ()

CLAZZES = [ ImageSize, ]