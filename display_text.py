from server import PromptServer
import json

def decode_nested_json(json_):
    if not json_: return {}
    def ld(s):
        try: return json.loads(str(s))
        except json.decoder.JSONDecodeError: return s
        except: pass 
    return { k:ld(json_[k]) for k in json_ } if isinstance(json_,dict) else json_

class DisplayText:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return {"required" : {},
                "optional" : { "string": ("STRING", {"default":"", "forceInput":True}), "json_": ("JSON", {"default":"", "forceInput":True}), },
                "hidden": { "id": "UNIQUE_ID" } }
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "func"
    OUTPUT_NODE = True

    def func(self, id, string=None, json_=None):
        text = string if string is not None else json.dumps(decode_nested_json(json_), indent=2)
        PromptServer.instance.send_sync("cg.quicknodes.textmessage", {"id": id, "message":text})
        #print(f"{id}:{text}")
        return ()
    
class DisplayList(DisplayText):
    @classmethod    
    def INPUT_TYPES(s):
        return {"required" : {"string": ("STRING", {"default":"", "forceInput":True}), },
                "hidden": { "id": "UNIQUE_ID" } }
    INPUT_IS_LIST = True
    FUNCTION = "_func"
    def _func(self, id, string):
        return self.func(id, string="\n".join(string))


class ExtractFromJson:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return {"required" : { "json_" : ("JSON", {}), "key" : ("STRING", {"default":"prompt"})}}
    RETURN_TYPES = ("STRING",)
    FUNCTION = "func"

    def func(self, json_, key):
        if isinstance(json_,str): json_ = json.loads(json_)
        return (decode_nested_json(json_).get(key,""),)
    
class DisplayLength:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return {"required" : {},
                "optional" : { "anything": ("*", {"default":"", "forceInput":True}), },
                "hidden": { "id": "UNIQUE_ID" } }
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "func"
    OUTPUT_NODE = True

    def func(self, id, anything=""):
        try:
            text = f"{len(anything)}"
        except:
            text = "doesn't support __len__"
        PromptServer.instance.send_sync("cg.quicknodes.textmessage", {"id": id, "message":text})
        #print(f"{id}:{text}")
        return ()
    
CLAZZES = [DisplayText, DisplayLength, DisplayList, ExtractFromJson]