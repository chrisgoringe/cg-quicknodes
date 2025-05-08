import json
from ui_decorator import ui_signal
from strings import decode_nested_json

class DisplayBase:
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "func"

@ui_signal(['display_text'])
class DisplayText(DisplayBase):
    CATEGORY = "quicknodes/strings"
    @classmethod    
    def INPUT_TYPES(s):
        return {"required" : {},
                "optional" : { "string": ("STRING", {"default":"", "forceInput":True}), "json_": ("JSON", {"default":"", "forceInput":True}), }}
    INPUT_IS_LIST = True

    def func(self, string=None, json_=None):
        entries =  [s for s in string] if string is not None else []
        entries += [json.dumps(decode_nested_json(j), indent=2) for j in json_] if json_ is not None else []
        text = "\n".join(entries) if entries else ""
        return (text,)

    
CLAZZES = [DisplayText,]