from server import PromptServer
import json

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
        def ld(s):
            try: return json.loads(str(s))
            except json.decoder.JSONDecodeError: return s
            except:
                pass
        j = { k:ld(json_[k]) for k in json_ } if json_ and isinstance(json_,dict) else json_
        text = string or json.dumps(j, indent=2)
        PromptServer.instance.send_sync("cg.quicknodes.textmessage", {"id": id, "message":text})
        print(f"{id}:{text}")
        return ()
    
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
        print(f"{id}:{text}")
        return ()
    
CLAZZES = [DisplayText, DisplayLength]