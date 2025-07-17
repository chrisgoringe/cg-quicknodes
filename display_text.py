import json
from ui_decorator import ui_signal
from strings import decode_nested_json
from comfy.comfy_types.node_typing import IO

@ui_signal(['display_text'])
class DisplayText:
    CATEGORY = "quicknodes/strings"
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "func"

    @classmethod    
    def INPUT_TYPES(s):
        return {"required" : {},
                "optional" : { 
                    "string": ("STRING", {"default":"", "forceInput":True}), 
                    "json_": ("JSON", {"default":"", "forceInput":True}), 
                    "anything": (IO.ANY, {}),
                }}
    INPUT_IS_LIST = True

    def func(self, string=None, json_=None, anything=None):
        entries = []
        if string is not None:   entries += [s for s in string]
        if json_ is not None:    entries += [json.dumps(decode_nested_json(j), indent=2) for j in json_]
        if anything is not None: entries += [str(a) for a in anything]
        text = "\n".join(entries) if entries else ""
        return (text,)

CLAZZES = [DisplayText,]